import os
from dataclasses import dataclass

import httpx
from fastapi import HTTPException
from loggers.logger_req import logger

COUNTRY_URL = "https://api.restcountries.com/countries/v5"
API_KEY = os.environ.get("COUNTRY_API_KEY")

if not API_KEY:
    raise ValueError("COUNTRY_API_KEY environment variable is not set")

@dataclass
class CountryInfo:
    capital: str
    currency_code: str
    currency_name: str

def handing_best_similarity(objects, country_name):
    item = None
    for country in objects:
        if country.get("names", {}).get("common").casefold() == country_name.casefold():
            item = country
            break
    return item

async def get_country_info(country_name: str) -> CountryInfo:
    logger.debug(f"Getting country info for {country_name}")
    params = {
        "q": country_name,
        "limit": 10
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(COUNTRY_URL, params=params, headers={"Authorization": f"Bearer {API_KEY}"})
    except httpx.RequestError as exc:
        logger.error(f"Countries service unreachable: {exc}")
        raise HTTPException(status_code=502, detail="Countries service unreachable") from exc
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetch country: {exc}")
        raise HTTPException(status_code=500, detail="Error fetching country") from exc
    data = response.json()
    objects = data.get("data", {}).get("objects", [])
    if not objects:
        logger.warning(f"Country {country_name} not found")
        raise HTTPException(status_code=400, detail=f"Country {country_name} not found")
    item = handing_best_similarity(objects, country_name)
    try:
        capital = item["capitals"][0]["name"]
        currency_code = item["currencies"][0]["code"]
        currency_name = item["currencies"][0]["name"]
    except (KeyError, TypeError) as exc:
        logger.error(f"Invalid response format: {exc}")
        raise HTTPException(status_code=502, detail="Invalid response format") from exc
    return CountryInfo(
        capital=capital,
        currency_code=currency_code,
        currency_name=currency_name
    )
