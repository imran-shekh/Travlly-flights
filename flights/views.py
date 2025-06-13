from django.shortcuts import render
import os
import requests
from dotenv import load_dotenv
from .models import FlightOffer
from datetime import datetime

load_dotenv()


def search_flights(request):
    flights_data = []

    if request.method == 'GET' and 'origin' in request.GET:
        origin = request.GET.get('origin').upper()
        destination = request.GET.get('destination').upper()
        date = request.GET.get('date')

        # Fetch access token from Amadeus
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("AMADEUS_CLIENT_ID"),
            "client_secret": os.getenv("AMADEUS_CLIENT_SECRET"),
        }
        token_response = requests.post(token_url, data=token_data)
        access_token = token_response.json().get("access_token")

        if access_token:
            search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": date,
                "adults": 1,
                "currencyCode": "INR"
            }


            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                flights = data.get("data", [])

                for item in flights:
                    try:
                        itinerary = item["itineraries"][0]["segments"][0]
                        airline = itinerary["carrierCode"]
                        flight_number = itinerary["number"]
                        price = item["price"]["total"]
                        currency = item["price"]["currency"]
                        departure_time = itinerary["departure"]["at"]


                        arrival_time = itinerary["arrival"]["at"]

                        # Convert strings to datetime objects
                        fmt = "%Y-%m-%dT%H:%M:%S"
                        departure_dt = datetime.strptime(departure_time, fmt)
                        arrival_dt = datetime.strptime(arrival_time, fmt)

                        duration = arrival_dt - departure_dt  # timedelta object
                        duration_str = str(duration)


                        # Avoid duplicates: check if flight already saved
                        if not FlightOffer.objects.filter(
                            origin=origin,
                            destination=destination,
                            departure_date=date,
                            airline=airline,
                            flight_number=flight_number,
                            price=price,
                            currency=currency
                        ).exists():
                            FlightOffer.objects.create(
                                origin=origin,
                                destination=destination,
                                departure_date=date,
                                airline=airline,
                                flight_number=flight_number,
                                price=price,
                                currency=currency,
                                duration=duration_str
                            )
                    except Exception as e:
                        print("Error saving flight:", e)

        # Fetch only today's search result from DB
        flights_data = FlightOffer.objects.filter(
            origin=origin,
            destination=destination,
            departure_date=date
        )

    return render(request, "search.html", {"flights": flights_data})
