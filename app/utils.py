import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_key=OPENAI_API_KEY)

def classify_technology_company(description: str) -> bool:
    prompt = PromptTemplate(
        input_variables=["description"],
        template="Based on the following company description, is this a technology company? Answer with Yes or No.\n\nDescription: {description}\n\nAnswer:"
    )

    response = llm(prompt.format(description=description))
    return response.strip().lower() == "yes"