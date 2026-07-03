from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)


from dotenv import load_dotenv
import os
import uuid

load_dotenv()

EMBEDDING_DIMENSION = 256
COLLECTION_NAME = "pdf_rag"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)



def create_collection():

    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )


    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="session_id",
        field_schema="keyword"
    )



def upsert_vectors(chunks, vectors, session_id):
    points = []

    for chunk, vector in zip(chunks, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "session_id": session_id,
                    "text": chunk.page_content,
                }
            )
        )


    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    

def search_vectors(query_vector, session_id, limit):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="session_id",
                    match=MatchValue(value=session_id)
                )
            ]
        ),
        limit=limit
    )

    return results.points


def delete_vectors(session_id):
    client.delete(
    collection_name=COLLECTION_NAME,
    points_selector=Filter(
        must=[
            FieldCondition(
                key="session_id",
                match=MatchValue(value=session_id)
            )
        ]
    )
)
    
"""client.delete_collection(
    collection_name="pdf_rag"
)"""