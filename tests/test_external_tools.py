from unittest.mock import AsyncMock, MagicMock, patch

from app.core.external_tools import get_exchange_rate



def _make_fake_httpx_response(json_data: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    return response

@patch("app.core.external_tools.httpx.AsyncClient")
async def test_get_exchange_rate_returns_rate_on_success(mock_client_cls):
    fake_response = _make_fake_httpx_response(
        {"result": "success", "rates": {"UAH": 41.5}}
    )
    mock_client = AsyncMock
    mock_client.get = AsyncMock(return_value=fake_response)
    mock_client_cls.return_value.__aenter__.return_value = mock_client

    result = await get_exchange_rate("usd", "uah")

    assert result == {"base": "USD", "target": "UAH", "rate": 41.5}




@patch("app.core.external_tools.httpx.AsyncClient")
async def test_get_exchange_rate_handles_unknown_target_currency(mock_client_cls):
    fake_response = _make_fake_httpx_response(
        {"result": "success", "rates": {"EUR": 0.9}}
    )

    mock_client = AsyncMock
    mock_client.get = AsyncMock(return_value=fake_response)
    mock_client_cls.return_value.__aenter__.return_value = mock_client

    result = await get_exchange_rate("usd", "XXX")

    assert "error" in result


@patch("app.core.external_tools.httpx.AsyncClient")
async def test_get_exchange_rate_handles_api_failure(mock_client_cls):
    fake_response = _make_fake_httpx_response(
        {"result": "error"}
    )
    mock_client = AsyncMock
    mock_client.get = AsyncMock(return_value=fake_response)
    mock_client_cls.return_value.__aenter__.return_value = mock_client

    result = await get_exchange_rate("USD", "UAH")

    assert "error" in result
