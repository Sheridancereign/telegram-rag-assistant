from unittest.mock import AsyncMock, MagicMock, patch

from app.core.rag_engine import generate_answer


def _make_fake_response(text: str) -> MagicMock:
    response = MagicMock()
    response.text = text
    return response

@patch("app.core.rag_engine._client")
async def test_generate_answer_returns_model_text(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_make_fake_response("London is a capital of England")
    )
    answer = await generate_answer("What is the capital of England?",["London is a capital of England"])
    assert answer == "London is a capital of England"

@patch("app.core.rag_engine._client")
async def test_generate_answer_includes_question_and_context_in_prompt(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_make_fake_response("response")
    )
    await generate_answer("My question?", ["Chunk 1", "Chunk 2"])

    call_kwargs = mock_client.aio.models.generate_content.call_args.kwargs
    prompt = call_kwargs["contents"]

    assert "My question?" in prompt
    assert "Chunk 1" in prompt
    assert "Chunk 2" in prompt



@patch("app.core.rag_engine._client")
async def test_generate_answer_joins_multiple_chunks_with_separator(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_make_fake_response("response")
    )
    await generate_answer("question?", ["Chunk 1", "Chunk 2"])

    prompt = mock_client.aio.models.generate_content.call_args.kwargs["contents"]

    assert "Chunk 1\n\n---\n\nChunk 2" in prompt