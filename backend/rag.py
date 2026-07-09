'''
This file contains the code for Retrieval Augmented Generation (RAG). The vector 
database used for this project is ChromaDB
'''

import chromadb

from backend.config import CHROMA_PATH, COLLECTION_NAME, N_RESULTS

chroma_client = chromadb.PersistentClient(path = CHROMA_PATH)
collection = chroma_client.get_collection(name = COLLECTION_NAME)

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


def retrieve_context(question):
    results = collection.query(
        query_texts=[question],
        n_results=N_RESULTS
    )

    context = build_context(results)

    sources = []

    for metadata in results["metadatas"][0]:
        sources.append({
            "source": metadata["source"],
            "page": metadata["page"]
        })

    return context, sources