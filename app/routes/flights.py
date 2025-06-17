from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"


async def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_CLIENT_ID,
        "client_secret": AMADEUS_CLIENT_SECRET
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(AMADEUS_TOKEN_URL, data=payload)

    try:
        data = response.json()
        return data["access_token"]
    except Exception as e:
        return None


async def fetch_flights(origin, destination, date, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "currencyCode": "INR",
        "max": 5
    }

    async def fetch_flights(origin, destination, date, token):
        headers = {
        "Authorization": f"Bearer {token}",
    }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "currencyCode": "INR",
        "max": 5
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(AMADEUS_FLIGHT_SEARCH_URL, headers=headers, params=params)
        data = response.json()

    print("📦 Amadeus Response:", data)  # <-- Add this line to debug

    offers = []

    if "data" not in data:
        return []   # ✅ Just return an empty list

    for flight in data["data"]:
        try:
            segment_first = flight["itineraries"][0]["segments"][0]
            segment_last = flight["itineraries"][0]["segments"][-1]

            dep_time_full = segment_first["departure"]["at"]  # Full ISO datetime
            arr_time_full = segment_last["arrival"]["at"]

            offer = {
                "airline": flight["validatingAirlineCodes"][0],
                "departure": segment_first["departure"]["iataCode"],
                "arrival": segment_last["arrival"]["iataCode"],
                "departure_time": dep_time_full,
                "arrival_time": arr_time_full,
                "price": flight["price"]["total"],
                "duration": flight["itineraries"][0]["duration"].replace("PT", "").replace("H", "h ").replace("M", "m").strip()
            }
            offers.append(offer)
        except Exception as e:
            continue

    return offers   # ✅ Always return list of offers




@router.get("/search")
async def search(origin: str, destination: str, date: str):
    token = await get_access_token()

    outbound_flights = await fetch_flights(origin, destination, date, token)

    return_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    return_flights = await fetch_flights(destination, origin, return_date, token)

    return {"outbound": outbound_flights, "return": return_flights}
