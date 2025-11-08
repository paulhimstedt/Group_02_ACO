# modules/travel_times.py

import json
import googlemaps
from time import sleep
from config import GOOGLE_MAPS_API_KEY, TRAVEL_MODE

def build_travel_time_matrix(markets, delay=0.3):
    """Builds a travel time matrix using Google Maps API."""
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    matrix = {"times": {}}
    
    # --- DEBUGGING: Get total number of pairs for progress ---
    total_pairs = len(markets) * (len(markets) - 1)
    current_pair = 0
    print(f"📈 Total pairs to calculate: {total_pairs}")
    # --- END DEBUGGING ---

    for m1 in markets:
        matrix["times"][m1.id] = {}
        for m2 in markets:
            if m1.id == m2.id:
                continue
                

            current_pair += 1
            print(f"\nProcessing pair {current_pair}/{total_pairs}: {m1.name} → {m2.name}")

                
            # Check if coordinates exist for both markets
            if not all([m1.latitude, m1.longitude, m2.latitude, m2.longitude]):

                print(f"  [SKIPPED] Missing coordinates.")
                print(f"    - {m1.name}: ({m1.latitude}, {m1.longitude})")
                print(f"    - {m2.name}: ({m2.latitude}, {m2.longitude})")

                matrix["times"][m1.id][m2.id] = None
                continue

            origin = (m1.latitude, m1.longitude)
            dest = (m2.latitude, m2.longitude)
            

            print(f"  [API CALL] Origin: {origin} | Dest: {dest} | Mode: {TRAVEL_MODE}")


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

                    print(f"  [SUCCESS] Duration: {duration:.1f} minutes")

                else:
                    matrix["times"][m1.id][m2.id] = None

                    print(f"  [NO RESULT] API returned no route.")

            except Exception as e:

                print(f"  [ERROR] {e}")

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