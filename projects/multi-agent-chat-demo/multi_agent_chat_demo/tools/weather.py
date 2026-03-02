"""Weather tool using Open-Meteo API with Braintrust tracing."""

import httpx
from braintrust import traced


@traced
async def get_coordinates(city: str) -> tuple[float, float]:
    """
    Geocode city name to coordinates using Open-Meteo Geocoding API.

    Args:
        city: City name to geocode

    Returns:
        Tuple of (latitude, longitude)

    Raises:
        ValueError: If city not found
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            raise ValueError(f"City '{city}' not found")

        result = data["results"][0]
        return result["latitude"], result["longitude"]


@traced
async def get_weather(latitude: float, longitude: float) -> dict:
    """
    Fetch current weather from Open-Meteo API.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Dictionary with weather data including temperature, wind speed, and weather code
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,weather_code,relative_humidity_2m",
                "timezone": "auto",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})

        # Map weather codes to descriptions
        weather_code = current.get("weather_code", 0)
        weather_desc = _get_weather_description(weather_code)

        return {
            "temperature": current.get("temperature_2m"),
            "temperature_unit": data.get("current_units", {}).get("temperature_2m", "°C"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": data.get("current_units", {}).get("wind_speed_10m", "km/h"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": data.get("current_units", {}).get("relative_humidity_2m", "%"),
            "weather_code": weather_code,
            "weather_description": weather_desc,
            "timezone": data.get("timezone", "UTC"),
        }


def _get_weather_description(code: int) -> str:
    """
    Map WMO weather codes to human-readable descriptions.

    Reference: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return weather_codes.get(code, "Unknown")


@traced
async def get_weather_for_city(city: str) -> dict:
    """
    Get weather for a city by name (combines geocoding + weather fetch).

    Args:
        city: City name

    Returns:
        Dictionary with weather data and location info
    """
    # Geocode city
    latitude, longitude = await get_coordinates(city)

    # Get weather
    weather = await get_weather(latitude, longitude)

    # Add location info
    weather["city"] = city
    weather["latitude"] = latitude
    weather["longitude"] = longitude

    return weather


@traced
def format_weather_response(weather_data: dict) -> str:
    """
    Format weather data into a human-readable response.

    Args:
        weather_data: Weather data dictionary from get_weather_for_city()

    Returns:
        Formatted weather report string
    """
    city = weather_data.get("city", "Unknown location")
    temp = weather_data.get("temperature")
    temp_unit = weather_data.get("temperature_unit", "°C")
    wind = weather_data.get("wind_speed")
    wind_unit = weather_data.get("wind_speed_unit", "km/h")
    humidity = weather_data.get("humidity")
    humidity_unit = weather_data.get("humidity_unit", "%")
    description = weather_data.get("weather_description", "Unknown")

    return (
        f"🌤️ Weather in {city}:\n"
        f"   Condition: {description}\n"
        f"   Temperature: {temp}{temp_unit}\n"
        f"   Wind Speed: {wind} {wind_unit}\n"
        f"   Humidity: {humidity}{humidity_unit}"
    )
