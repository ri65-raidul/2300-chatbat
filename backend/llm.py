'''
This file contains the code that interacts with a Large Language Model (LLM). For this
project, we are using Gemini. The Gemini API Key can be found in .env file. 

'''

import os
from dotenv import load_dotenv
from google import genai

from backend.config import GEMINI_MODEL

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key is None:
    raise ValueError("GEMINI_API_KEY was not found. Check your .env file.")

client = genai.Client(api_key=api_key)

def ask_gemini(question, context):
    prompt = f"""
You are an AI teaching assistant for Cornell University's ECE2300.

Answer the student's question using ONLY the provided course documents.

Rules:
- You may use simple reasoning based on the context, such as:
  - counting listed people/items
  - comparing dates
  - summarizing a list
  - doing basic arithmetic
- Do not use outside knowledge.
- Do not make up policies, names, deadlines, or requirements.
- If the answer cannot be determined from the context, say:
  "I couldn't find that information in the provided course documents."
- Keep answers concise and student-friendly.

    Question: 
    {question}

    Context:
    {context}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text