from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import os
import pandas as pd
from dotenv import load_dotenv
import httpx  # Import httpx for making HTTP requests
from llama_index.llms.groq.base import Groq  # Make sure this path is correct
from llama_index.experimental.query_engine import PandasQueryEngine


# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL")

def clean_and_process_data(df):
    """
    Cleans and processes procurement data, addressing missing values,
    standardizing formats, and enhancing performance with type conversions.
    
    Args:
        df (pd.DataFrame): Input raw DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned and processed DataFrame.
    """
    # Drop unnecessary columns
    columns_to_drop = [
        'LPA Number', 'Requisition Number', 'Sub-Acquisition Type', 
        'Sub-Acquisition Method', 'Supplier Qualifications', 
        'Supplier Zip Code', 'Classification Codes', 'Commodity Title', 
        'Location', 'Normalized UNSPSC', 'Class', 'Class Title', 
        'Family', 'Family Title', 'Segment', 'Segment Title'
    ]
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Handle missing values
    df['Supplier Code'] = df['Supplier Code'].fillna(0).astype(float)
    df['Supplier Name'] = df['Supplier Name'].fillna("N/A").astype("string")
    df['Item Name'] = df['Item Name'].fillna("N/A").astype("string")
    df['Item Description'] = df['Item Description'].fillna("N/A").astype("string")

    # Optimize Purchase Order Number by converting to category
    df['Purchase Order Number'] = df['Purchase Order Number'].astype('category')

    # Drop duplicates based on Purchase Order Number
    df.drop_duplicates(subset=['Purchase Order Number'], inplace=True)

    # Parse dates
    if "Purchase Date" in df.columns:
        df['Purchase Date'] = pd.to_datetime(
            [date[:-4] + '20' + date[-2:] if isinstance(date, str) else date for date in df['Purchase Date']],
            errors='coerce'
        )
    if "Creation Date" in df.columns:
        df['Creation Date'] = pd.to_datetime(df['Creation Date'], format='%d/%m/%Y', errors='coerce')

    # Standardize Fiscal Year format
    if "Fiscal Year" in df.columns:
        df["Fiscal Year"] = df["Fiscal Year"].apply(lambda x: f"FY{x}" if "FY" not in str(x) else x).astype("category")

    # Convert appropriate columns to categories for better performance
    categorical_columns = [
        "Acquisition Type", "Acquisition Method", "Department Name", "CalCard"
    ]
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Clean and convert numeric columns
    for col in ["Unit Price", "Total Price"]:
        if col in df.columns:
            df[col] = df[col].replace('[\\$,]', '', regex=True).astype(float).fillna(0)

    # Recalculate Total Price
    if all(col in df.columns for col in ["Quantity", "Unit Price", "Total Price"]):
        df["Total Price"] = df["Quantity"] * df["Unit Price"]

    return df

def generate_context(df):
    """
    Generates context for the LLM by summarizing the dataset structure and 
    including a sample of the data.
    
    Args:
        df (pd.DataFrame): The DataFrame to summarize.
        
    Returns:
        str: A string representation of the dataset summary and sample.
    """
    # Dataset summary
    context = "Dataset Summary:\n"
    context += f"Number of rows: {len(df)}\n"
    context += f"Number of columns: {len(df.columns)}\n"
    context += "Column details:\n"
    for col in df.columns:
        context += f" - {col}: {df[col].dtype}, {df[col].nunique()} unique values\n"

    # Add a sample of the data
    context += "\nSample Data:\n"
    context += df.head(5).to_string(index=False)

    return context

def chat(message: str):
    """
    Processes a user query using the PandasQueryEngine.

    Args:
        message (str): User input query.

    Returns:
        str: Response from the query engine.
    """
    try:
        # Initialize the PandasQueryEngine only once
        llm = Groq(model=model, api_key=api_key)

        # Load and preprocess the dataset
        df = pd.read_csv(r"C:\Users\dell\Desktop\chatbot\PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv")
        df = clean_and_process_data(df)

        # Generate context from the DataFrame
        context = generate_context(df)

        # Initialize the query engine
        query_engine = PandasQueryEngine(df=df, llm=llm, verbose=True)

        # Combine context with the user query
        formatted_query = f"{context}\n\nUser Query: {message}"

        # Query the PandasQueryEngine
        response = query_engine.query(formatted_query)

        return response.response  # Return the raw response
    except Exception as e:
        # Handle and report errors
        return f"An error occurred: {str(e)}"


app = FastAPI(title="Procurement Chatbot API")
router = APIRouter()

chat_history: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    request: str

@router.post("/chat/submit/{chat_id}")
async def submit_chat(chat_id: str, chat_request: ChatRequest):
    # Get the response from the chat function
    response = chat(chat_request.request)

    # Send the response to the /process-data endpoint
    async with httpx.AsyncClient() as client:
        process_response = await client.post(
            "http://127.0.0.1:8000/api/v1/process-data",  # Adjust the URL if needed
            json={"message": response}
        )
        process_data = process_response.json()

    # Store the history
    chat_history.setdefault(chat_id, []).append({"role": "user", "message": chat_request.request})
    chat_history[chat_id].append({"role": "assistant", "message": response})

    # Return the processed data
    return JSONResponse(content=process_data)


@router.get("/chat/history/{chat_id}")
def get_chat_history(chat_id: str):
    return JSONResponse(content=chat_history.get(chat_id, []))


@router.delete("/chat/history/{chat_id}")
def delete_chat_history(chat_id: str):
    if chat_id in chat_history:
        del chat_history[chat_id]
    return JSONResponse(content={"message": "Chat history deleted."})



@router.post("/process-data")
async def process_data(data: dict):
    # Extract the message from the incoming data
    message = data.get("message", "")
    
    # Ensure message is non-empty
    if not message:
        return {"error": "No message provided in the data"}

    # Split the message into lines, ensuring no empty lines
    lines = [line for line in message.split("\n") if line.strip()]
    
    # Split each line by the last space to separate the label and numeric value
    records = [line.rsplit(" ", 1) for line in lines]
    
    # Create a DataFrame with two columns: the first column is the label, the second is the numeric value
    df = pd.DataFrame(records, columns=["Label", "Value"])
    
    # Remove unwanted rows where the Label is "Department" or contains "Name: Purchase Order Number, dtype:"
    df = df[~df["Label"].isin(["Department", "Name: Purchase Order Number, dtype:"])]
    
    # Convert "Value" column to numeric and format to avoid scientific notation
    df["Value"] = pd.to_numeric(df["Value"], errors='coerce')

    # Format the numeric values (you can adjust the formatting as needed)
    df["Value"] = df["Value"].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "N/A")
    
    # Remove rows where 'Value' is "N/A"
    df = df[df["Value"] != "N/A"]
    
    # Convert the DataFrame to a dictionary for easy consumption by the frontend
    response_data = df.to_dict(orient="records")

    # Ensure proper response format
    return {"data": response_data}
app.include_router(router, prefix="/api/v1")
