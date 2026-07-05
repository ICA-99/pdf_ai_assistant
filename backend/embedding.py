from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

def create_embeddings(chunks, output_dimensionality):

    texts = [chunk.page_content for chunk in chunks]

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config={
            "output_dimensionality": output_dimensionality
        }
    )

    vectors = [embedding.values for embedding in result.embeddings]

    return vectors



def create_query_embedding(query, output_dimensionality):

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query]
,
        config={
            "output_dimensionality": output_dimensionality
        }
    )

    return result.embeddings[0].values
