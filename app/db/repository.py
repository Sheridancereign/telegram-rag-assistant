import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk, User


async def get_or_create_user(session: AsyncSession, telegram_id: int) -> User:
    user = await session.get(User, telegram_id)
    if user is None:
        user = User(id=telegram_id)
        session.add(user)
        await session.flush()
    return user


async def create_document(
    session: AsyncSession,
    user_id: int,
    file_name: str,
) -> Document:
    document = Document(user_id=user_id, file_name=file_name)
    session.add(document)
    await session.flush()
    return document


async def save_chunks(
    session: AsyncSession,
    document_id: uuid.UUID,
    texts: list[str],
    embeddings: list[list[float]],
) -> list[DocumentChunk]:
    if len(texts) != len(embeddings):
        raise ValueError("texts and embeddings must have the same length")

    chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_text=text,
            chunk_index=index,
            embedding=embedding,
        )
        for index, (text, embedding) in enumerate(zip(texts, embeddings))
    ]
    session.add_all(chunks)
    await session.flush()
    return chunks


async def search_similar_chunks(
    session: AsyncSession,
    document_id: uuid.UUID,
    query_embedding: list[float],
    limit: int = 3,
) -> list[DocumentChunk]:
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_latest_document(session: AsyncSession, user_id: int) -> Document | None:
    stmt = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()