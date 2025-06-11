from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
AMADEUS_AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_SEARCH_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

# Store fetched flights in this array
flights_array = []


async def get_access_token():
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_API_KEY,
            "client_secret": AMADEUS_API_SECRET
        }
        response = await client.post(AMADEUS_AUTH_URL, data=data, headers=headers)
        return response.json()["access_token"]


@router.get("/api/search")
async def search_flights(origin: str, destination: str, date: str):
    global flights_array
    token = await get_access_token()

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "nonStop": False,
        "currencyCode": "INR",
        "max": 5
    }

    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(AMADEUS_FLIGHT_SEARCH_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        # Save in array
        flights_array = data["data"]
        return {"message": "Flights fetched successfully", "flights": flights_array}
    else:
        return JSONResponse(content={"error": "Failed to fetch flights", "details": response.text}, status_code=400)
