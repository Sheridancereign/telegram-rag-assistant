from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я RAG-ассистент.\n\n"
        "Пришли мне PDF или TXT документ, а затем задавай вопросы по его содержимому."
    )