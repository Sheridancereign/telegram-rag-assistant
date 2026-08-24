from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rag_engine import generate_agentic_answer
from app.core.tools import build_tool_dispatch
from app.db.repository import get_latest_document


router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def handle_question(message: Message, session: AsyncSession) -> None:
    document = await get_latest_document(session, message.from_user.id)
    if document is None:
        await message.answer("Сначала пришли мне PDF или TXT документ.")
        return

    tool_dispatch = build_tool_dispatch(session, document.id)
    answer = await generate_agentic_answer(message.text, tool_dispatch)
    await message.answer(answer)