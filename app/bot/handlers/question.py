from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.embeddings import embed_query
from app.core.rag_engine import generate_answer
from app.db.repository import get_latest_document, search_similar_chunks

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_question(message: Message, session: AsyncSession) -> None:
    document = await get_latest_document(session, message.from_user.id)
    if document is None:
        await message.answer("Сначала пришли мне PDF или TXT документ.")
        return

    query_embedding = await embed_query(message.text)
    chunks = await search_similar_chunks(session, document.id, query_embedding)

    if not chunks:
        await message.answer("Не нашёл релевантной информации в документе.")
        return

    answer = await generate_answer(message.text, [c.chunk_text for c in chunks])
    await message.answer(answer)