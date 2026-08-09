from google import genai

from app.config import settings


GENERATION_MODEL = "gemini-3.6-flash"

_client = genai.Client(api_key=settings.gemini_api_key)


PROMPT_TEMPLATE = """\
Ответь на вопрос пользователя, опираясь ТОЛЬКО на предоставленный контекст ниже.
Если в контексте нет ответа — честно скажи, что не нашёл информации в документе.

Контекст:
{context}

Вопрос: {question}
"""


async def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    response = await _client.aio.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )
    return response.text