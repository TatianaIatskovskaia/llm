import requests
import os

URL = 'https://api.apilayer.com/fixer/latest'
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise RuntimeError("API_KEY is not set")


def get_exchange_rate(from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    try:
        resp = requests.get(URL, params={'base': from_currency, 'symbols': to_currency}, headers={'apikey': API_KEY})
    except requests.RequestException:
        return f"Could not reach the exchange rate service to check {from_currency} to {to_currency}"
    data = resp.json()
    if resp.status_code != 200 or not data.get('success', True):
        return f"Could not get exchange rate for {from_currency} to {to_currency}"
    rate = data.get('rates', {}).get(to_currency)
    if rate is None:
        return f"{to_currency} is not valid currency"

    return f"one {from_currency} = {rate} {to_currency}"


TOOLS = {
    'get_exchange_rate': get_exchange_rate
}