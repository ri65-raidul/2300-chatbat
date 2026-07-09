import pdfplumber
import chromadb

# Creating a Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Creating a collection
collection = chroma_client.get_or_create_collection(name="my_collection")


# Dictionary to hold the chunk
chunks = []

#Chunking the pdf
with pdfplumber.open("documents/ece2300_sp26_syllabus.pdf") as pdf:
    for page in pdf.pages:

        text = page.extract_text() # preserving line breaks

        # Handling empty pages
        if text is None:
            continue

        lines = text.split('\n')

        chunk_number = 0

        # Looping through 10 lines at a time
        for i in range(0, len(lines), 10):
            chunk_lines = lines[i:i+10]
            chunk_text = "\n".join(chunk_lines)

            chunk_id = f"syllabus_p{page.page_number}_{chunk_number}"

            chunks.append({
                "id"   : chunk_id,
                "text" : chunk_text,
                "page" : page.page_number,
                "chunk": chunk_number
            })

            chunk_number += 1

# Printing out the chunks
#for c in chunks:
    #print(c["id"])
    #print(c["text"])
    #print("----")



# Storing into Chromadb
collection.upsert(
    ids=[chunk["id"] for chunk in chunks],
    documents=[chunk["text"] for chunk in chunks],
    metadatas=[
        {
            "page": chunk["page"],
            "chunk": chunk["chunk"],
            "source": "ece2300_sp26_syllabus.pdf"
        }
        for chunk in chunks
    ]
)


#Testing retrieval
question = "What is the late homework policy?"

results = collection.query(
    query_texts=[question],
    n_results=3
)

print("\nQUESTION: ")
print(question)

print("\nTOP MATCHES: ")
for i in range(len(results["documents"][0])):
    print("Result", i + 1)
    print("ID", results["ids"][0][i])
    print("Metadata: ", results["metadatas"][0][i])
    print("Text: ")
    print(results["documents"][0][i])
    print("----")