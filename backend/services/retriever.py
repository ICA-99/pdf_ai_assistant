from backend.services.pdf_loader import load_pdf
from backend.services.chunker import documents_chunker
from backend.services.embedding import create_embeddings, create_query_embedding
from backend.services.vector_store import upsert_vectors, search_vectors

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq


model = ChatGroq(model="llama-3.1-8b-instant")


def process_pdf(pdf_name: str, user_id: str):

    documents = load_pdf(pdf_name)

    chunks = documents_chunker(documents)

    vectors = create_embeddings(
        chunks,
        output_dimensionality=256
    )

    upsert_vectors(
        chunks=chunks,
        vectors=vectors,
        user_id=user_id,
        pdf_id=pdf_name
    )

    return {
        "message": "PDF processed successfully"
    }


def chat_with_pdf(
    user_query: str,
    user_id: str,
    pdf_id: str,
    limit: int = 2
):
    query_vector = create_query_embedding(
        query=user_query,
        output_dimensionality=256
    )

    output = search_vectors(
        query_vector=query_vector,
        user_id=user_id,
        pdf_id=pdf_id,
        limit=limit
    )

    context = "\n\n".join(
        point.payload["text"]
        for point in output
    )

    prompt = ChatPromptTemplate.from_template("""
        Answer only from the provided context.
        If the user asks a greeting or general question,
        reply normally.

        If the answer is not in the context,
        say "I do not know the answer."

        Context:
        {context}

        Question:
        {user_query}
        
    """)

    chain = prompt | model

    response = chain.invoke({
        "context": context,
        "user_query": user_query
    })

    return response.content