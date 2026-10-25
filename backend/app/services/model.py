from functools import lru_cache
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to backend/.env "
            "before starting a research run."
        )

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0,
        api_key=api_key,
    )
