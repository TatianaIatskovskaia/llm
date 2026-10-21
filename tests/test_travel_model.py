import pytest
from pydantic import ValidationError
from models.travel_model import TravelInfoRequest, TravelInfoResponse

def test_travel_info_request_requires_all_fields():
    with pytest.raises(ValidationError):
        TravelInfoRequest(country_from="France")

def test_travel_info_request():
    request = TravelInfoRequest(
        country_from="USA",
        country_to="Canada",
        is_capital=True,
        is_weather=True,
        is_currency=True
    )
    assert request.country_from == "USA"
    assert request.country_to == "Canada"
    assert request.is_capital == True
    assert request.is_weather == True
    assert request.is_currency == True


@pytest.fixture
def request_data():
    return {
        "country_from": "USA",
        "country_to": "Canada",
        "is_capital": True,
        "is_weather": False,
        "is_currency": True,
    }


@pytest.mark.parametrize(
    "field", ["country_from", "country_to", "is_capital", "is_weather", "is_currency"]
)
def test_request_rejects_each_missing_field(request_data, field):
    del request_data[field]

    with pytest.raises(ValidationError) as exc_info:
        TravelInfoRequest(**request_data)

    assert [(error["loc"], error["type"]) for error in exc_info.value.errors()] == [
        ((field,), "missing")
    ]


@pytest.mark.parametrize(
    "field,value,error_type",
    [
        ("country_from", None, "string_type"),
        ("country_to", 123, "string_type"),
        ("is_capital", None, "bool_type"),
        ("is_weather", "sometimes", "bool_parsing"),
        ("is_currency", 2, "bool_parsing"),
    ],
)
def test_request_rejects_invalid_values(request_data, field, value, error_type):
    request_data[field] = value

    with pytest.raises(ValidationError) as exc_info:
        TravelInfoRequest(**request_data)

    assert exc_info.value.errors()[0]["loc"] == (field,)
    assert exc_info.value.errors()[0]["type"] == error_type


def test_request_serialization_preserves_false_flags(request_data):
    request = TravelInfoRequest(**request_data)

    assert request.model_dump() == request_data
    assert TravelInfoRequest.model_validate_json(request.model_dump_json()) == request


@pytest.mark.parametrize("field", ["country_from", "country_to"])
def test_response_requires_each_country(field):
    data = {"country_from": "USA", "country_to": "Canada"}
    del data[field]

    with pytest.raises(ValidationError) as exc_info:
        TravelInfoResponse(**data)

    assert exc_info.value.errors()[0]["loc"] == (field,)
    assert exc_info.value.errors()[0]["type"] == "missing"


def test_response_defaults_optional_fields_to_none():
    response = TravelInfoResponse(country_from="USA", country_to="Canada")

    assert response.model_dump() == {
        "country_from": "USA",
        "country_to": "Canada",
        "capital": None,
        "weather": None,
        "currency_code_from": None,
        "currency_code_to": None,
        "currency_name_from": None,
        "currency_name_to": None,
        "exchange_rate": None,
    }


def test_response_with_all_fields_round_trips_through_json():
    data = {
        "country_from": "USA",
        "country_to": "Canada",
        "capital": "Ottawa",
        "weather": "Sunny, 20°C",
        "currency_code_from": "USD",
        "currency_code_to": "CAD",
        "currency_name_from": "US Dollar",
        "currency_name_to": "Canadian Dollar",
        "exchange_rate": 1.37,
    }
    response = TravelInfoResponse(**data)

    assert response.model_dump() == data
    assert TravelInfoResponse.model_validate_json(response.model_dump_json()) == response


@pytest.mark.parametrize("field", ["currency_code_from", "currency_code_to"])
@pytest.mark.parametrize(
    "code,error_type",
    [("", "string_too_short"), ("US", "string_too_short"), ("USDD", "string_too_long")],
)
def test_response_rejects_currency_codes_outside_three_characters(field, code, error_type):
    with pytest.raises(ValidationError) as exc_info:
        TravelInfoResponse(country_from="USA", country_to="Canada", **{field: code})

    assert exc_info.value.errors()[0]["loc"] == (field,)
    assert exc_info.value.errors()[0]["type"] == error_type


@pytest.mark.parametrize(
    "field",
    [
        "capital",
        "weather",
        "currency_code_from",
        "currency_code_to",
        "currency_name_from",
        "currency_name_to",
        "exchange_rate",
    ],
)
def test_response_accepts_explicit_none_for_optional_fields(field):
    response = TravelInfoResponse(country_from="USA", country_to="Canada", **{field: None})

    assert getattr(response, field) is None


@pytest.mark.parametrize(
    "field,value,error_type",
    [
        ("country_from", None, "string_type"),
        ("country_to", None, "string_type"),
        ("capital", [], "string_type"),
        ("weather", {}, "string_type"),
        ("currency_code_from", 123, "string_type"),
        ("currency_code_to", 123, "string_type"),
        ("currency_name_from", [], "string_type"),
        ("currency_name_to", {}, "string_type"),
        ("exchange_rate", "unknown", "float_parsing"),
    ],
)
def test_response_rejects_invalid_field_types(field, value, error_type):
    data = {"country_from": "USA", "country_to": "Canada", field: value}

    with pytest.raises(ValidationError) as exc_info:
        TravelInfoResponse(**data)

    assert exc_info.value.errors()[0]["loc"] == (field,)
    assert exc_info.value.errors()[0]["type"] == error_type
