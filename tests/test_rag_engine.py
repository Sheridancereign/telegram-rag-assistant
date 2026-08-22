from unittest.mock import AsyncMock, MagicMock, patch

from app.core.rag_engine import generate_agentic_answer


def _make_tool_call_response(tool_name: str, args: dict) -> MagicMock:
    function_call = MagicMock()
    function_call.name = tool_name
    function_call.args = args

    response = MagicMock()
    response.function_calls = [function_call]
    response.candidates = [MagicMock()]
    return response


def _make_final_response(text: str) -> MagicMock:
    response = MagicMock()
    response.function_calls = []
    response.text = text
    return response


@patch("app.core.rag_engine._client")
async def test_direct_answer_without_tool_calls(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_make_final_response("Hello! How can i help you?")
    )
    answer = await generate_agentic_answer("Hello!", [])
    assert answer == "Hello! How can i help you?"
    assert mock_client.aio.models.generate_content.call_count == 1

@patch("app.core.rag_engine._client")
async def test_single_tool_call_round_trip(mock_client):
    tool_fn = AsyncMock(return_value={"chunks": ["some fragment"]})
    tool_dispatch = {"search_knowledge_base": tool_fn}

    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[
            _make_tool_call_response("search_knowledge_base", {"query": "test"}),
            _make_final_response("answer based on some fragment")
            ]
    )

    answer = await generate_agentic_answer("What's my tech stack?", tool_dispatch)

    assert answer == "answer based on some fragment"
    tool_fn.assert_awaited_once_with(query="test")
    assert mock_client.aio.models.generate_content.call_count == 2


@patch("app.core.rag_engine._client")
async def test_unknown_tool_name_produces_error_and_continues(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[
            _make_tool_call_response("nonexistent_tool", {}),
            _make_final_response("Sorry, could not generate answer")
            ]
    )

    answer = await generate_agentic_answer("question", tool_dispatch={})

    assert answer == "Sorry, could not generate answer"

@patch("app.core.rag_engine._client")
async def test_tool_exception_is_caught_and_reported_to_model(mock_client):
    failing_tool = AsyncMock(side_effect=RuntimeError("Service is unavailable"))
    tool_dispatch = {"get_exchange_rate": failing_tool}

    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=[
            _make_tool_call_response("get_exchange_rate", {"base_currency": "USD", "target_currency": "UAH"}),
            _make_final_response("Cannot get exchange rate")
            ]
    )
    answer = await generate_agentic_answer("What's the exchange rate?", tool_dispatch)

    assert answer == "Cannot get exchange rate"
    failing_tool.assert_awaited_once()


@patch("app.core.rag_engine._client")
async def test_exceeding_max_rounds_returns_fallback(mock_client):
    tool_fn = AsyncMock(return_value={"result": "Something"})
    tool_dispatch = {"search_knowledge_base": tool_fn}

    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_make_tool_call_response("search_knowledge_base", {"query": "cycled"})
    )

    answer = await generate_agentic_answer("question", tool_dispatch)

    assert answer == "Не удалось сформировать ответ за отведённое количество шагов."
    assert mock_client.aio.models.generate_content.call_count == 5