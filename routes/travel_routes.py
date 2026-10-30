from fastapi import APIRouter, HTTPException, Request

from cache import get_last_pair, set_last_pair
from models.travel_model import TravelInfoRequest, TravelInfoResponse
from services.countries import get_country_info
from services.weather import get_weather
from services.currency import get_exchange_rate

router = APIRouter(prefix="/travel")

ALL_TRUE_FLAGS = {"is_capital": True, "is_weather": True, "is_currency": True}

async def build_travel_info(
        country_from: str,
        country_to: str,
        is_capital: bool,
        is_weather: bool,
        is_currency: bool,
) -> TravelInfoResponse:
    country_to_info = None
    if is_capital or is_currency or is_weather:
        country_to_info = await get_country_info(country_to)
    country_from_info = None
    if is_currency:
        country_from_info = await get_country_info(country_from)
    weather = None
    if is_weather:
        weather = await get_weather(country_to_info.capital)
    exchange_rate = None
    if is_currency:
        exchange_rate = await get_exchange_rate(country_from_info.currency_code, country_to_info.currency_code)

    return TravelInfoResponse(
        country_from=country_from,
        country_to=country_to,
        capital=country_to_info.capital if is_capital else None,
        weather=weather,
        currency_code_from=country_from_info.currency_code if is_currency else None,
        currency_code_to=country_to_info.currency_code if is_currency else None,
        currency_name_from=country_from_info.currency_name if is_currency else None,
        currency_name_to=country_to_info.currency_name if is_currency else None,
        exchange_rate=exchange_rate,
    )

@router.post("/info", response_model=TravelInfoResponse)
async def post_travel_info(payload: TravelInfoRequest, request: Request) -> TravelInfoResponse:
    request.state.travel_flags = {
        "is_capital": payload.is_capital,
        "is_weather": payload.is_weather,
        "is_currency": payload.is_currency,
    }
    result = await build_travel_info(
        payload.country_from,
        payload.country_to,
        is_capital=payload.is_capital,
        is_weather=payload.is_weather,
        is_currency=payload.is_currency,
    )
    set_last_pair(payload.country_from, payload.country_to)
    return result

@router.get("/info", response_model=TravelInfoResponse)
async def get_travel_info(
        request: Request,
        country_from: str | None = None,
        country_to: str | None = None,
) -> TravelInfoResponse:
    request.state.travel_flags = ALL_TRUE_FLAGS
    if (country_from is None) != (country_to is None):
        raise HTTPException(status_code=400, detail="Both country_from and country_to must be provided together")
    if country_from is None and country_to is None:
        cached = get_last_pair()
        if cached is None:
            raise HTTPException(status_code=400, detail="No previous pair found")
        country_from, country_to = cached
    return await build_travel_info(country_from, country_to, **request.state.travel_flags)