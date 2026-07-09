import os
import chromadb
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key is None:
    raise ValueError("GEMINI_API_KEY was not found. Check your .env file")

client = genai.Client(api_key=api_key)


def build_context(results):
    context = ""

    for i in range(len(results["documents"][0])):
        source = results["metadatas"][0][i]["source"]
        page = results["metadatas"][0][i]["page"]
        text = results["documents"][0][i]

        context += f"[Document {i+1}] Source: {source}, Page: {page}\n"
        context += text
        context += "\n\n"

    return context


def ask_gemini(question, context):
    prompt = f"""
You are an AI teaching assistant for Cornell University's ECE2300 (Digital Logic and Computer Organization).

Your job is to answer students' questions accurately using ONLY the provided course documents.

Instructions:
- Answer only using information contained in the provided context.
- If the context does not contain enough information, say:
  "I couldn't find that information in the provided course documents."
- Do not make up policies or assumptions.
- Keep answers concise and easy for students to understand.
- When appropriate, cite the page number where the information was found.

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


# Connect to Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Load the existing collection
collection = chroma_client.get_collection(name="my_collection")

print("ECE2300 Chatbot")
print("Type 'exit' to quit.\n")


while True:
    question = input("Ask a question: ")

    # Exit
    if question.lower() == "exit":
        break

    results = collection.query(
        query_texts = [question],
        n_results=5
    )

    context = build_context(results)

    try:
        answer = ask_gemini(question, context)
        print("\nANSWER:\n")
        print(answer)

    except Exception as e:
        print(f"\nError Calling Gemini:\n{e}")
