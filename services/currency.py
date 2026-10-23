import os
import httpx
from fastapi import HTTPException
from loggers.logger_req import logger

FIXER_URL = "https://api.apilayer.com/fixer/convert"
API_KEY = os.getenv("FIXER_API_KEY")

if not API_KEY:
    raise ValueError("FIXER_API_KEY environment variable is not set")

async def get_exchange_rate(code_from: str, code_to: str) -> float:
    logger.debug(f"Fetching exchange rate from {code_from} to {code_to}")
    params = {
        "from": code_from,
        "to": code_to,
        "amount": 1
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(FIXER_URL, params=params, headers={"apikey": API_KEY})
    except httpx.RequestError as exc:
        logger.error(f"Currency service unreachable: {exc}")
        raise HTTPException(status_code=502, detail="Currency service unreachable") from exc
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching currency exchange rate: {exc}")
        raise HTTPException(status_code=500, detail="Error fetching currency exchange rate") from exc
    data = response.json()
    if not data.get("success", False):
        logger.warning(f"Exchange rate from {code_from} to {code_to} not found")
        raise HTTPException(status_code=400, detail=f"Exchange rate from {code_from} to {code_to} not found")
    try:
        return data ["info"]["rate"]
    except (KeyError, TypeError) as exc:
        logger.error(f"Invalid response format: {exc}")
        raise HTTPException(status_code=502, detail="Invalid response format") from exc