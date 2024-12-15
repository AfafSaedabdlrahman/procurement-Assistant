import os
import pandas as pd
from dotenv import load_dotenv
from llama_index.llms.groq.base import Groq
from llama_index.experimental.query_engine import PandasQueryEngine
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Load API keys and model
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("LLM_MODEL")

# Load and preprocess the dataset
df = pd.read_csv(r"C:\Users\dell\Desktop\chatbot\PURCHASE ORDER DATA EXTRACT 2012-2015_0.csv")
df.drop_duplicates(inplace=True)
df['Total Price'] = df['Total Price'].replace('[\$,]', '', regex=True).astype(float).fillna(0)
df['Unit Price'] = df['Unit Price'].replace('[\$,]', '', regex=True).astype(float).fillna(0)
df['Purchase Date'] = pd.to_datetime(
    [date[:-4] + '20' + date[-2:] if isinstance(date, str) else date for date in df['Purchase Date']]
)
df['Creation Date'] = pd.to_datetime(df['Creation Date'], format='%d/%m/%Y', errors='coerce')

# Input model for FastAPI
class QueryRequest(BaseModel):
    user_query: str

# Chat function to handle user queries
def chat(user_query):
    def generate_prompt(user_query):
        prompt = f"""
        You are a powerful language model that can translate natural language queries into valid pandas commands for data analysis. Your task is to convert the user's query into a corresponding pandas command that performs the requested operation on the DataFrame. 

        **Important:** return the correct pandas command, and the result of the command.

        **Instructions:**
        1. Analyze the natural language query and determine the type of operation requested (e.g., filtering, aggregating, sorting, summarizing).
        2. Convert the details into a pandas command, making sure it is syntactically correct.
        3. Only return the pandas command in your response, without any explanation or additional text.

        **User Query:**
        {user_query}

        **Pandas Command (only return the command below):**
        """
        return prompt

    llm = Groq(model=model, api_key=api_key)
    query_engine = PandasQueryEngine(df=df, verbose=False, llm=llm, synthesize_response=True)

    prompt = generate_prompt(user_query)
    response = query_engine.query(prompt)

    if hasattr(response, 'text'):
        pandas_command = response.text.strip()
    else:
        pandas_command = str(response).strip()

    if not pandas_command.startswith("df"):
        raise ValueError(f"Invalid pandas command: {pandas_command}")

    result = eval(pandas_command)
    return pandas_command, result

@app.post("/query")
async def query(request: QueryRequest):
    try:
        pandas_command, result = chat(request.user_query)
        return {
            "pandas_command": pandas_command,
            "result": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the query.")
