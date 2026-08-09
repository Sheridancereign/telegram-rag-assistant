import io

from aiogram import F, Router
from aiogram.types import Message
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.chunker import split_into_chunks
from app.core.embeddings import embed_document_chunks
from app.db.repository import create_document, get_or_create_user, save_chunks

router = Router()


def _extract_text(file_bytes: bytes, file_name: str) -> str:
    if file_name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    return text.replace("\x00", "")


@router.message(F.document)
async def handle_document(message: Message, session: AsyncSession) -> None:
    document = message.document
    if not document.file_name.lower().endswith((".pdf", ".txt")):
        await message.answer("Пока поддерживаются только PDF и TXT файлы.")
        return

    await message.answer("Обрабатываю документ...")

    file = await message.bot.get_file(document.file_id)
    file_bytes_io = await message.bot.download_file(file.file_path)
    file_bytes = file_bytes_io.read()

    text = _extract_text(file_bytes, document.file_name)
    if not text.strip():
        await message.answer("Не удалось извлечь текст из документа.")
        return

    chunks = split_into_chunks(text)
    embeddings = await embed_document_chunks(chunks)

    await get_or_create_user(session, message.from_user.id)
    db_document = await create_document(session, message.from_user.id, document.file_name)
    await save_chunks(session, db_document.id, chunks, embeddings)
    await session.commit()

    await message.answer(
        f"Готово! Документ разбит на {len(chunks)} чанков и проиндексирован.\n"
        "Теперь можешь задавать вопросы по его содержимому."
    )