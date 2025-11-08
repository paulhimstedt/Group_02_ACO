# modules/coordinates.py

import googlemaps
from config import GOOGLE_MAPS_API_KEY

def fetch_coordinates(markets):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    for market in markets:
        # Skip if market already has coordinates
        if market.latitude and market.longitude:
            print(f"{market.name}: Already has coordinates")
            continue

        if not market.url:
            print(f"No URL for {market.name}, skipping coordinate fetch.")
            continue
            
        try:
            result = gmaps.find_place(
                input=market.url,
                input_type="textquery", 
                fields=["geometry/location"]
            )
            if result["candidates"]:
                loc = result["candidates"][0]["geometry"]["location"]
                market.latitude = loc["lat"]
                market.longitude = loc["lng"]
                print(f"✔ {market.name}: {market.latitude}, {market.longitude}")
            else:
                print(f"No location found for {market.name}")
        except Exception as e:
            print(f"Error fetching {market.name}: {e}")
    return markets