# modules/coordinates.py

import googlemaps
from config import GOOGLE_MAPS_API_KEY

def fetch_coordinates(markets):
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    for market in markets:
        try:
            result = gmaps.find_place(
                input=market.url,
                input_type="url",
                fields=["geometry/location"]
            )
            if result["candidates"]:
                loc = result["candidates"][0]["geometry"]["location"]
                market.lat = loc["lat"]
                market.lon = loc["lng"]
                print(f"✔ {market.name}: {market.lat}, {market.lon}")
            else:
                print(f"⚠ No location found for {market.name}")
        except Exception as e:
            print(f"❌ Error fetching {market.name}: {e}")
    return markets
