import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

mcp = FastMCP("Weather MCP Server")
app = mcp  # Alias for module-relative import options

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

REQUEST_TIMEOUT_SECONDS = 20


def _get_api_key() -> str:
    if not OPENWEATHER_API_KEY:
        raise RuntimeError(
            "OPENWEATHER_API_KEY is missing from the project .env file."
        )

    return OPENWEATHER_API_KEY


def _request_json(
    url: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        details = ""

        failed_response = getattr(
            exc,
            "response",
            None,
        )

        if failed_response is not None:
            details = f" Response: {failed_response.text[:500]}"

        raise RuntimeError(
            f"OpenWeather request failed: {exc}.{details}"
        ) from exc


@mcp.tool()
def get_current_weather(
    city: str,
) -> dict[str, Any]:
    """Return the current weather for a city with mock fallback."""
    city = city.strip() or "Destination"

    try:
        data = _request_json(
            "https://api.openweathermap.org/data/2.5/weather",
            {
                "q": city,
                "appid": _get_api_key(),
                "units": "metric",
            },
        )

        return {
            "city": data["name"],
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
        }
    except Exception as exc:
        return {
            "city": city,
            "temperature_c": 22.0,
            "feels_like_c": 22.5,
            "humidity": 60,
            "condition": "Mild and pleasant (Offline/Mock data)",
            "wind_speed": 4.5,
            "note": f"Live weather API offline ({exc}). Used fallback response.",
        }


@mcp.tool()
def get_forecast(
    city: str,
) -> dict[str, Any]:
    """Return the first five forecast entries for a city with mock fallback."""
    city = city.strip() or "Destination"

    try:
        data = _request_json(
            "https://api.openweathermap.org/data/2.5/forecast",
            {
                "q": city,
                "appid": _get_api_key(),
                "units": "metric",
            },
        )

        forecast = [
            {
                "datetime": item["dt_txt"],
                "temperature_c": item["main"]["temp"],
                "condition": item["weather"][0]["description"],
            }
            for item in data.get("list", [])[:5]
        ]

        return {
            "city": data.get("city", {}).get("name", city),
            "forecast": forecast,
        }
    except Exception as exc:
        return {
            "city": city,
            "forecast": [
                {"datetime": "Day 1 12:00", "temperature_c": 22.0, "condition": "Clear sky"},
                {"datetime": "Day 2 12:00", "temperature_c": 23.5, "condition": "Partly cloudy"},
                {"datetime": "Day 3 12:00", "temperature_c": 21.0, "condition": "Sunny"},
            ],
            "note": f"Live forecast API offline ({exc}). Used fallback response.",
        }


if __name__ == "__main__":
    # mcp_client.py launches this as a stdio subprocess.
    mcp.run(transport="stdio")
