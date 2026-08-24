import httpx

EXCHANGE_RATE_API_URL = "https://open.er-api.com/v6/latest/{base}"


async def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    base = base_currency.upper()
    target = target_currency.upper()

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(EXCHANGE_RATE_API_URL.format(base=base))
        response.raise_for_status()
        data = response.json()

    if data.get("result") != "success":
        return {"error": f"Failed to get exchange rate for {base}"}

    rates = data.get("rates", {})
    if target not in rates:
        return {"error": f"currency {target} was not found"}

    return {
        "base": base,
        "target": target,
        "rate": rates[target],
    }