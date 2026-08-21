from unittest.mock import AsyncMock, patch

from app.core.external_tools import get_exchange_rate
from app.core.tools import GET_EXCHANGE_RATE_DECLARATION, SEARCH_KNOWLEDGE_BASE_DECLARATION, build_tool_dispatch
from app.db.repository import create_document, get_or_create_user, save_chunks


FAKE_EMBEDDING_DIM = 768

def _fake_vector(seed: float) -> list[float]:
    return [seed] * FAKE_EMBEDDING_DIM

def test_tool_declarations_have_required_fields():
    assert SEARCH_KNOWLEDGE_BASE_DECLARATION.name == "search_knowledge_base"
    assert "query" in SEARCH_KNOWLEDGE_BASE_DECLARATION.parameters_json_schema["required"]

    assert GET_EXCHANGE_RATE_DECLARATION.name == "get_exchange_rate"
    required = GET_EXCHANGE_RATE_DECLARATION.parameters_json_schema["required"]
    assert "base_currency" in required
    assert "target_currency" in required


async def test_dispatch_contains_both_tools(session):
    user = await get_or_create_user(session, 999001)
    document = await create_document(session, user.id, "test.pdf")

    dispatch = build_tool_dispatch(session, document.id)

    assert "search_knowledge_base" in dispatch
    assert "get_exchange_rate" in dispatch
    assert dispatch["get_exchange_rate"] is get_exchange_rate


@patch("app.core.tools.embed_query")
async def test_search_knowledge_base_returns_matching_chunks(mock_embed_query, session):
    mock_embed_query.return_value = _fake_vector(1.0)

    user = await get_or_create_user(session, 999002)
    document = await create_document(session, user.id, "test.pdf")
    await save_chunks(session, document.id, ["релевантный чанк"], [_fake_vector(1.0)])

    dispatch = build_tool_dispatch(session, document.id)
    result = await dispatch["search_knowledge_base"]("любой вопрос")

    assert result == {"chunks": ["релевантный чанк"]}


@patch("app.core.tools.embed_query")
async def test_search_knowledge_base_returns_message_when_no_chunks(mock_embed_query, session):
    mock_embed_query.return_value = _fake_vector(1.0)

    user = await get_or_create_user(session, 999003)
    document = await create_document(session, user.id, "empty.pdf")

    dispatch = build_tool_dispatch(session, document.id)
    result = await dispatch["search_knowledge_base"]("вопрос без ответа")

    assert "result" in result


