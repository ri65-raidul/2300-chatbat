import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if api_key is None:
    raise ValueError("ANTHROPIC_API_KEY was not found. Check your .env file.")

client = Anthropic(api_key=api_key)

def ask_claude(question, context):
    prompt = f"""
You are an AI teaching assistant for Cornell University's ECE2300.

Answer the student's question using ONLY the provided course documents.

Rules:
- You may use simple reasoning based on the context.
- Do not use outside knowledge.
- Do not invent policies, names, deadlines, or requirements.
- If the answer cannot be determined from the context, say:
  "I couldn't find that information in the provided course documents."
- Keep answers concise and student-friendly.

Question:
{question}

Context:
{context}
"""

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    text_blocks = [
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]

    if not text_blocks:
        raise RuntimeError("Claude returned no text response.")

    return "\n".join(text_blocks)