from google import genai
from google.genai import types
import numpy as np

from app.config import settings

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768

_client = genai.Client(api_key=settings.gemini_api_key)



def _normalize(vector: list[float]) -> list[float]:
    array = np.array(vector)
    norm = np.linalg.norm(array)
    return (array / norm).tolist() if norm > 0 else vector

async def embed_document_chunks(chunks: list[str]) -> list[list[float]]:
    response = await _client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=chunks,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    return [_normalize(embedding.values) for embedding in response.embeddings]


async def embed_query(text: str) -> list[float]:
    response = await _client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    return _normalize(response.embeddings[0].values)