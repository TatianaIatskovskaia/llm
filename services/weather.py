import os
import httpx
from fastapi import HTTPException
from loggers.logger_req import logger

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("WEATHER_API_KEY")

if not API_KEY:
    raise ValueError("WEATHER_API_KEY environment variable is not set")

async def get_weather(city: str) -> str:
    logger.debug(f"Fetching weather for {city}")
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(WEATHER_URL, params=params)
    except httpx.RequestError as exc:
        logger.error(f"Weather service unreachable: {exc}")
        raise HTTPException(status_code=502, detail="Weather service unreachable") from exc
    if response.status_code == 404:
        logger.warning(f"City not found: {city}")
        raise HTTPException(status_code=404, detail=f"City {city} not found")
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching weather for {city}: {exc}")
        raise HTTPException(status_code=500, detail="Error fetching weather") from exc
    weather_data = response.json()
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    condition = weather_data["weather"][0]["description"]
    return f"Weather in {city}: {condition}, Temperature: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s"
