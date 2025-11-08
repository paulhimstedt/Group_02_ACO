# modules/travel_times.py

import json
import googlemaps
from time import sleep
from config import GOOGLE_MAPS_API_KEY, TRAVEL_MODE

def build_travel_time_matrix(markets, delay=0.3):
    """Builds a travel time matrix using Google Maps API."""
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    matrix = {"times": {}}

    for m1 in markets:
        matrix["times"][m1.id] = {}
        for m2 in markets:
            if m1.id == m2.id:
                continue
            origin = (m1.latitude, m1.longitude)
            dest = (m2.latitude, m2.longitude)

            try:
                result = gmaps.directions(
                    origin,
                    dest,
                    mode=TRAVEL_MODE,
                    departure_time="now"
                )
                if result:
                    duration = result[0]['legs'][0]['duration']['value'] / 60  # Minuten
                    matrix["times"][m1.id][m2.id] = round(duration, 1)
                else:
                    matrix["times"][m1.id][m2.id] = None
            except Exception as e:
                print(f"❌ {m1.name} → {m2.name}: {e}")
                matrix["times"][m1.id][m2.id] = None

            sleep(delay)

    return matrix

def save_travel_times(matrix, filepath):
    """Save travel time matrix to JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)

def load_travel_times(filepath):
    """Load travel times JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
