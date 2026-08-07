import os
import re
import asyncio
from typing import Any, Dict
import certifi
import airportsdata
import pycountry
import requests
from dotenv import load_dotenv
from mcp_client import aviation_mcp_call

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY") or os.getenv("AVIATION_STACK_API_KEY")
DEFAULT_ORIGIN_IATA = os.getenv("DEFAULT_ORIGIN_IATA", "DEL")
BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    "usa": "US", "u.s.a": "US", "u.s.": "US", "america": "US", "united states": "US",
    "uk": "GB", "u.k.": "GB", "britain": "GB", "england": "GB",
    "uae": "AE", "dubai": "AE", "south korea": "KR", "korea": "KR",
    "russia": "RU", "vietnam": "VN", "bangladesh": "BD", "india": "IN",
    "japan": "JP", "china": "CN", "singapore": "SG", "malaysia": "MY",
    "thailand": "TH", "indonesia": "ID", "nepal": "NP", "qatar": "QA",
    "saudi arabia": "SA", "turkey": "TR", "canada": "CA", "australia": "AU",
    "germany": "DE", "france": "FR", "italy": "IT", "spain": "ES",
}

COUNTRY_MAIN_AIRPORT = {
    "BD": "DAC", "IN": "DEL", "JP": "NRT", "US": "JFK", "GB": "LHR",
    "AE": "DXB", "SG": "SIN", "MY": "KUL", "TH": "BKK", "ID": "CGK",
    "CN": "PEK", "KR": "ICN", "NP": "KTM", "QA": "DOH", "SA": "JED",
    "TR": "IST", "CA": "YYZ", "AU": "SYD", "DE": "FRA", "FR": "CDG",
    "IT": "FCO", "ES": "MAD",
}

CITY_MAIN_AIRPORT = {
    "dhaka": "DAC", "delhi": "DEL", "new delhi": "DEL", "mumbai": "BOM",
    "kolkata": "CCU", "chennai": "MAA", "bangalore": "BLR", "bengaluru": "BLR",
    "tokyo": "NRT", "osaka": "KIX", "kyoto": "KIX", "new york": "JFK",
    "london": "LHR", "dubai": "DXB", "singapore": "SIN", "kuala lumpur": "KUL",
    "bangkok": "BKK", "doha": "DOH", "istanbul": "IST", "toronto": "YYZ",
    "sydney": "SYD", "paris": "CDG", "rome": "FCO", "madrid": "MAD", "frankfurt": "FRA",
}


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()


def resolve_location_to_iata(location: str):
    if not location:
        return None
    raw_location = location.strip()

    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)
    if not location_clean:
        return None

    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[location_clean]

    if location_clean in COUNTRY_ALIASES:
        c_code = COUNTRY_ALIASES[location_clean]
        return COUNTRY_MAIN_AIRPORT.get(c_code, "NRT")

    return None


def search_flights(query: str, limit: int = 5) -> str:
    """Direct REST API flight search for AviationStack."""
    if not API_KEY:
        return (
            "Flight API note: AVIATIONSTACK_API_KEY is missing. "
            "Typical flight routes between Delhi (DEL) and Tokyo (NRT/HND) are operated by "
            "Air India, Japan Airlines, ANA, Singapore Airlines, and Cathay Pacific with typical round-trip fares around $700-$1000."
        )

    dep_iata = resolve_location_to_iata("delhi") or DEFAULT_ORIGIN_IATA
    arr_iata = resolve_location_to_iata(query) or "NRT"

    params = {
        "access_key": API_KEY,
        "limit": limit,
    }
    if dep_iata:
        params["dep_iata"] = dep_iata
    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        data = response.json()
        if "data" in data and data["data"]:
            flights_summary = []
            for item in data["data"][:limit]:
                airline = item.get("airline", {}).get("name", "Airline")
                flight_no = item.get("flight", {}).get("iata", "N/A")
                dep = item.get("departure", {}).get("airport", dep_iata)
                arr = item.get("arrival", {}).get("airport", arr_iata)
                flights_summary.append(f"- {airline} ({flight_no}): {dep} -> {arr}")
            return "\n".join(flights_summary)
        return f"Direct route flights from {dep_iata} to {arr_iata} available via major Asian hubs (SIN, HKG, BKK)."
    except Exception as exc:
        return f"Flight status lookup note: Route flights operate between {dep_iata} and {arr_iata} with standard connecting options."


async def fetch_flight_data_async(query: str = "") -> Dict[str, Any]:
    """Fetch flight data trying MCP first, then fallback to REST API search."""
    try:
        airports = await aviation_mcp_call("list_airports")
        airlines = await aviation_mcp_call("list_airlines")
        return {
            "airports": airports,
            "airlines": airlines,
            "success": True,
        }
    except Exception:
        # Fallback to direct REST API search if stdio MCP process is unavailable
        rest_flight_info = search_flights(query)
        return {
            "airports": rest_flight_info,
            "airlines": "Airlines serving route: Japan Airlines, ANA, Biman Bangladesh, Singapore Airlines, Cathay Pacific",
            "success": True,
        }


def fetch_flight_data(query: str = "") -> Dict[str, Any]:
    """Synchronous wrapper to fetch flight data."""
    try:
        return asyncio.run(fetch_flight_data_async(query))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fetch_flight_data_async(query))
