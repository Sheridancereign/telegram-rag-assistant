from typing import Awaitable, Callable
from uuid import UUID

from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.embeddings import embed_query
from app.core.external_tools import get_exchange_rate
from app.db.repository import search_similar_chunks

SEARCH_KNOWLEDGE_BASE_DECLARATION = types.FunctionDeclaration(
    name="search_knowledge_base",
    description=(
        "Ищет релевантные фрагменты в загруженном пользователем документе. "
        "Используй этот инструмент, когда вопрос касается содержимого документа."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Поисковый запрос, отражающий суть вопроса пользователя",
            },
        },
        "required": ["query"],
    },
)

GET_EXCHANGE_RATE_DECLARATION = types.FunctionDeclaration(
    name="get_exchange_rate",
    description=(
        "Получает актуальный курс обмена между двумя валютами. "
        "Используй, когда пользователь спрашивает про курс валют, конвертацию денег и т.п."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "base_currency": {
                "type": "string",
                "description": "Код базовой валюты, например USD",
            },
            "target_currency": {
                "type": "string",
                "description": "Код целевой валюты, например UAH",
            },
        },
        "required": ["base_currency", "target_currency"],
    },
)

TOOLS = types.Tool(
    function_declarations=[
        SEARCH_KNOWLEDGE_BASE_DECLARATION,
        GET_EXCHANGE_RATE_DECLARATION,
    ]
)


def build_tool_dispatch(
    session: AsyncSession,
    document_id: UUID,
) -> dict[str, Callable[..., Awaitable[dict]]]:
    """Собирает словарь {имя_инструмента: реальная_async_функция} с привязанным контекстом."""

    async def search_knowledge_base(query: str) -> dict:
        query_embedding = await embed_query(query)
        chunks = await search_similar_chunks(session, document_id, query_embedding)
        if not chunks:
            return {"result": "Ничего релевантного не найдено в документе."}
        return {"chunks": [chunk.chunk_text for chunk in chunks]}

    return {
        "search_knowledge_base": search_knowledge_base,
        "get_exchange_rate": get_exchange_rate,
    }