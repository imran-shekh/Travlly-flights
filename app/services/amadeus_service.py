import os
import datetime
import httpx
from dotenv import load_dotenv
from app.database.mongo import db

load_dotenv()

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
flights_collection = db["flights"]

# 1. Get Amadeus access token
async def get_access_token():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": AMADEUS_CLIENT_ID,
                    "client_secret": AMADEUS_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()["access_token"]
    except Exception as e:
        print("❌ Error getting token:", e)
        return None
# 2. Fetch flights using token
async def search_flights(origin, destination, date):
    token = await get_access_token()
    if not token:
        return []

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": date,
        "adults": 1,
        "max": 5
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            data = response.json()

            simplified_flights = []
            for offer in data.get("data", []):
                segment = offer["itineraries"][0]["segments"][0]
                flight = {
                    "flight_number": segment.get("carrierCode", "") + segment.get("number", ""),
                    "departure": segment["departure"].get("iataCode", ""),
                    "arrival": segment["arrival"].get("iataCode", ""),
                    "price": offer["price"]["total"]
                }
                simplified_flights.append(flight)

            await save_flights_to_db(simplified_flights)
            return simplified_flights
    except Exception as e:
        print("❌ Error fetching flights:", e)
        return []

async def save_flights_to_db(flights_data):
    for flight in flights_data:
        try:
            existing = await flights_collection.find_one({"flight_number": flight["flight_number"]})
            if not existing:
                flight["created_at"] = datetime.datetime.utcnow()
                await flights_collection.insert_one(flight)
        except Exception as e:
            print("❌ Error saving flight:", e)
