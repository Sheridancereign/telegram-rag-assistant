from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.embeddings import EMBEDDING_DIM, _normalize, embed_document_chunks, embed_query


def test_normalize_produces_unit_length_vector():
    vector = [3.0, 4.0]
    normalized = _normalize(vector)
    length = sum(x ** 2 for x in normalized) ** 0.5
    assert length == pytest.approx(1.0)



def test_normalize_handles_zero_vector():
    vector = [0.0, 0.0]
    assert _normalize(vector) == vector


def _make_fake_response(vectors: list[list[float]]) -> MagicMock:
    response = MagicMock()
    response.embeddings = [MagicMock(values=v) for v in vectors]
    return response


@patch("app.core.embeddings._client")
async def test_embed_query_returns_normalized_vector(mock_client):
    mock_client.aio.models.embed_content = AsyncMock(
        return_value=_make_fake_response([[1.0] * EMBEDDING_DIM])
    )

    result = await embed_query("test question")

    assert len(result) == EMBEDDING_DIM
    length = sum(x ** 2 for x in result) ** 0.5
    assert length == pytest.approx(1.0)


@patch("app.core.embeddings._client")
async def test_embed_document_chunks_preserves_order(mock_client):
    mock_client.aio.models.embed_content = AsyncMock(
        return_value=_make_fake_response([[1.0] * EMBEDDING_DIM, [2.0] * EMBEDDING_DIM])
    )

    result = await embed_document_chunks(["first chunk", "second chunk"])

    assert len(result) == 2
    mock_client.aio.models.embed_content.assert_called_once()


@patch("app.core.embeddings._client")
async def test_embed_document_chunks_splits_into_batches(mock_client):
    mock_client.aio.models.embed_content = AsyncMock(
        side_effect=lambda **kwargs: _make_fake_response(
            [[1.0] * EMBEDDING_DIM for _ in kwargs["contents"]]
        )
    )

    chunks = [f"chunk {i}" for i in range(250)]
    result = await embed_document_chunks(chunks)

    assert len(result) == 250
    assert mock_client.aio.models.embed_content.call_count == 3