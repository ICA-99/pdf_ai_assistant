from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

import tempfile
import os
import uuid

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.services.pdf_loader import load_pdf
from backend.services.chunker import documents_chunker
from backend.services.embedding import create_embeddings, create_query_embedding
from backend.services.vector_store import (
    create_collection,
    upsert_vectors,
    search_vectors,
    delete_vectors,
)

load_dotenv()

app = FastAPI()

model = ChatGroq(
    model="llama-3.1-8b-instant"
)


@app.on_event("startup")
async def startup():
    create_collection()


@app.get("/")
async def home():
    return {"message": "Hello"}


# -----------------------------
# Upload PDF
# -----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    try:
        # Load PDF
        documents = load_pdf(temp_path)

        # Split into chunks
        chunks = documents_chunker(documents)

        # Create embeddings
        vectors = create_embeddings(
            chunks,
            output_dimensionality=256
        )

        # Unique session id
        session_id = str(uuid.uuid4())

        # Store vectors
        upsert_vectors(
            chunks=chunks,
            vectors=vectors,
            session_id=session_id
        )

        return {
            "session_id": session_id
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -----------------------------
# Request Models
# -----------------------------
class QueryRequest(BaseModel):
    session_id: str
    query: str


class DeleteRequest(BaseModel):
    session_id: str


# -----------------------------
# Delete Vectors
# -----------------------------
@app.post("/delete")
async def delete_pdf(request: DeleteRequest):

    delete_vectors(request.session_id)

    return {
        "message": "PDF deleted successfully."
    }


# -----------------------------
# Query PDF
# -----------------------------
@app.post("/query")
async def query_pdf(request: QueryRequest):

    query_vector = create_query_embedding(
        query=request.query,
        output_dimensionality=256
    )

    results = search_vectors(
        query_vector=query_vector,
        session_id=request.session_id,
        limit=3
    )

    if not results:
        return {
            "answer": "I could not find any relevant information in the uploaded PDF."
        }

    context = "\n\n".join(
        point.payload["text"]
        for point in results
    )

    prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Rules:
1. If the user greets you (Hi, Hello, etc.), respond normally.
2. Answer ONLY using the provided context.
3. If the answer is not in the context, reply:
   "I don't know based on the uploaded document."
4. Do not make up information.

Context:
{context}

Question:
{question}
""")

    chain = prompt | model

    response = chain.invoke(
        {
            "context": context,
            "question": request.query
        }
    )

    return {
        "answer": response.content
    }