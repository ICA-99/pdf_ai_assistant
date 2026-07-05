from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

import tempfile
import os
import uuid

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.pdf_loader import load_pdf
from backend.chunker import documents_chunker
from backend.embedding import create_embeddings, create_query_embedding
from backend.vector_store import (
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
    You are an enterprise-grade AI Document Assistant.

    Your primary responsibility is to answer the user's question ONLY from the retrieved document context.

    ========================
    ROLE
    ========================
    - You analyze the provided document context.
    - You provide accurate, concise, and professional answers.
    - Never use external knowledge.
    - Never guess or assume missing information.

    ========================
    RESPONSE RULES
    ========================

    1. Greeting Handling
    - If the user sends only a greeting (such as "Hi", "Hello", "Good Morning", "Hey"), respond politely and briefly.
    - Do not mention the document unless the user asks a document-related question.

    2. Context Restriction
    - Every factual answer must come ONLY from the provided context.
    - Treat the provided context as the only source of truth.

    3. No Hallucination
    - Never fabricate facts.
    - Never infer information that is not explicitly supported by the context.
    - Never complete missing information using your own knowledge.
    - Never speculate.

    4. Unknown Information
    If the answer cannot be found in the provided context, or the context is insufficient, respond exactly with:

    "I don't know based on the uploaded document."

    Do not add explanations, assumptions, or alternative answers.

    5. Answer Quality
    - Be clear and professional.
    - Use complete sentences.
    - Preserve technical terms exactly as written in the document.
    - If the context contains lists, tables, or steps, present them in a clean, readable format.
    - If multiple relevant pieces of information exist, combine them into one coherent answer.
    - Keep the answer focused on the user's question.

    6. Citations
    - If the retrieved context contains page numbers or section names, include them naturally in your answer.
    - Do not invent page numbers.

    ========================
    CONTEXT
    ========================
    {context}

    ========================
    QUESTION
    ========================
    {question}

    ========================
    ANSWER
    ========================
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