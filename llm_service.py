import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm(provider="openai", model=None):
    """Get LLM based on provider"""
    if provider == "openai":
        model = model or "gpt-3.5-turbo"
        return ChatOpenAI(
            model=model,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
    elif provider == "groq":
        model = model or "llama3-8b-8192"
        return ChatGroq(
            model=model,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")