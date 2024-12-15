import os
import pandas as pd
from dotenv import load_dotenv
from llama_index.llms.groq.base import Groq
from llama_index.experimental.query_engine import PandasQueryEngine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL")

# Initialize FastAPI
app = FastAPI()

# Initialize query history
query_history = []

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

# Load and preprocess the dataset
df = pd.read_csv(r"C:\Users\dell\Desktop\chatbot\PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv")
df = clean_and_process_data(df)

# Initialize the PandasQueryEngine
llm = Groq(model=model, api_key=api_key)
query_engine = PandasQueryEngine(df=df, llm=llm, verbose=True)

# Define request model
class QueryRequest(BaseModel):
    user_query: str

# API Endpoint for user queries
@app.post("/query/")
async def handle_query(query: QueryRequest):
    try:
        user_query = query.user_query  # Extract the query from the request
        # Query the PandasQueryEngine
    
        
        # Generate context from the DataFrame
        context = generate_context(df)
        
        # Combine context with the user query
        formatted_query = f"{context}\n\nUser Query: {user_query}"

        # Query the PandasQueryEngine
        response = query_engine.query(formatted_query)

        # Log the query in the history
        query_log = {
            "query": user_query,
            "response": response.response,  # This contains the actual output of the query
        }
        query_history.append(query_log)

        return query_log
    except Exception as e:
        # Handle errors gracefully
        raise HTTPException(status_code=400, detail=str(e))

# API Endpoint to retrieve query history
@app.get("/history/")
async def get_query_history():
    return {"query_history": query_history}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
