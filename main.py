import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from chatbot import generate_response

load_dotenv()

GOOGLE_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
if not GOOGLE_PROJECT or not GOOGLE_LOCATION:
    raise RuntimeError("GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION not set in environment.")

app = FastAPI(title="Gemini Chatbot Agent")

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier for conversation history")
    question: str = Field(..., description="User’s question")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Agent’s answer")

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    try:
        answer = generate_response(req.session_id, req.question)
        return QueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))