from backend.rag import retrieve_context
from backend.llm import ask_gemini


def answer_question(question):
    context, sources = retrieve_context(question)
    answer = ask_gemini(question, context)

    return {
        "answer": answer,
        "sources": sources
    }