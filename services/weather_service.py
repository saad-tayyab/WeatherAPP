from typing import Optional, Tuple

import httpx
from httpx import Response

from infrastructure import weather_cache
from models.location import Location
from models.validation_error import ValidationError

api_key: Optional[str] = None


async def get_report(loc: Location, units: str) -> dict:
    city, state, country, units = validate_units(loc.city, loc.state, loc.country, units)

    if forecast := weather_cache.get_weather(loc.city, loc.state, loc.country, units):
        return forecast

    if loc.state:
        q = f'{loc.city},{loc.state},{loc.country}'
    else:
        q = f'{loc.city},{loc.country}'

    url = f'https://api.openweathermap.org/data/2.5/weather?q={q}&appid={api_key}&units={units}'

    async with httpx.AsyncClient() as client:
        resp: Response = await client.get(url)
        # resp.raise_for_status()
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)

    data = resp.json()
    forecast = data['main']
    # forecast = data

    weather_cache.set_weather(loc.city, loc.state, loc.country, units, forecast)
    return forecast


def validate_units(city: str, state: Optional[str], country: Optional[str], units: str) -> \
        Tuple[str, Optional[str], str, str]:
    city = city.lower().strip()
    if not country:
        country = "us"
    else:
        country = country.lower().strip()

    if len(country) != 2:
        error = f"Invalid country: {country}. It must be a two letter abbreviation such as US or GB."
        raise ValidationError(status_code=400, error_msg=error)

    if state:
        state = state.strip().lower()

    if state and len(state) != 2:
        error = f"Invalid state: {state}. It must be a two letter abbreviation such as CA or KS (use for US only)."
        raise ValidationError(status_code=400, error_msg=error)

    if units:
        units = units.strip().lower()

    valid_units = {'standard', 'metric', 'imperial'}
    if units not in valid_units:
        error = f"Invalid units '{units}', it must be one of {valid_units}."
        raise ValidationError(status_code=400, error_msg=error)

    return city, state, country, units
