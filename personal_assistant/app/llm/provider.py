import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from app.schemas.chat_schemas import IntentResponse

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0,
    api_key= os.getenv("GEMINI_API_KEY"),
    max_output_tokens=2000
)

llm_agent = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    api_key= os.getenv("GEMINI_API_KEY"),

)
rewiter_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0,
    api_key= os.getenv("GEMINI_API_KEY"),
    
)

intent_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key= os.getenv("GEMINI_API_KEY"),
    
)

intent_llm_structured =  intent_llm.with_structured_output(IntentResponse)

from openai import OpenAI
import os

rest_llm = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)













