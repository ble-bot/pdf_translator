from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from app.config import settings
from app.langchain.prompts import build_translation_prompt


def build_translation_chain() -> Runnable:
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.BASE_URL,
        max_retries=2,
        timeout=120,
    )

    prompt = build_translation_prompt()

    chain = prompt | llm | StrOutputParser()

    return chain
