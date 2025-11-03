import os
import uuid
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from constants import schema

# Load environment variables
load_dotenv()

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH", "10"))

if not PROJECT or not LOCATION:
    raise RuntimeError("Missing GOOGLE_CLOUD_PROJECT or GOOGLE_CLOUD_LOCATION")

# Initialize GenAI client using Vertex AI mode with ADC
client = genai.Client(
    vertexai=True,
    project=PROJECT,
    location=LOCATION
)

MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = SYSTEM_PROMPT + "Here is the schema of the table:" + schema

class SQLAnswer(BaseModel):
    sql: str = Field(description="A valid BigQuery SQL query. No backticks or code fences.")
    reason: str = Field(description="Brief explanation of how the query answers the question.")

if SYSTEM_PROMPT:
    system_cache = client.caches.create(
    model=MODEL_NAME,
    config={"system_instruction": SYSTEM_PROMPT}
    )
    SYSTEM_CACHE_NAME = system_cache.name  # reference to cached system context
else:
    SYSTEM_CACHE_NAME = None

history_store: dict[str, list[dict]] = {}


def generate_response(session_id: str, user_message: str) -> str:
    """
    Get a response from the Gemini model for the given user_message, 
    maintaining context for the specified session.
    """
    # Initialize session history if not present
    if session_id not in history_store:
        history_store[session_id] = []
    history = history_store[session_id]

    # Add the new user message to the history
    history.append({"role": "user", "content": user_message})
    # Enforce message limit (drop oldest messages if over limit)
    if len(history) > MAX_HISTORY_LENGTH:
        history_store[session_id] = history[-MAX_HISTORY_LENGTH:]  # keep only last N

    # Convert history into Gemini SDK content format (user vs model roles):contentReference[oaicite:5]{index=5}
    content_list = []
    for msg in history_store[session_id]:
        role = msg["role"]
        text = msg["content"]
        if role == "user":
            content_list.append(types.Content(role="user", parts=[types.Part(text=text)]))
        else:
            # Gemini uses role "model" for the assistant's responses:contentReference[oaicite:6]{index=6}
            content_list.append(types.Content(role="model", parts=[types.Part(text=text)]))

    # Call Gemini API to generate a reply, using cached system prompt for context:contentReference[oaicite:7]{index=7}:contentReference[oaicite:8]{index=8}
    print("The list is as follows:")
    print(content_list)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=content_list,
        config=types.GenerateContentConfig(cached_content=SYSTEM_CACHE_NAME, response_schema=SQLAnswer, response_mime_type="application/json"),
        #response_mime_type="application/json",
        #response_schema=SQLAnswer
    )
    answer = response.text  # the assistant's reply text

    # Add the assistant's answer to history
    history_store[session_id].append({"role": "assistant", "content": answer})
    if len(history_store[session_id]) > MAX_HISTORY_LENGTH:
        history_store[session_id] = history_store[session_id][-MAX_HISTORY_LENGTH:]

    print(response.text)

    return answer
