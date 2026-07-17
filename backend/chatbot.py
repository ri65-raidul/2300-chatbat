from backend.rag import retrieve_context
from backend.llm import ask_claude


def answer_question(question):
    context, sources = retrieve_context(question)
    answer = ask_claude(question, context)

    return {
        "answer": answer,
        "sources": sources
    }