# main.py

from modules.market_data import load_markets
from modules.travel_times import build_travel_time_matrix, save_travel_times

# Define file paths
MARKETS_JSON_INPUT_FILE = "data/real/markets.json"
TRAVEL_TIMES_OUTPUT_FILE = "data/real/travel_times.json"

def main():
    # 1. Load the markets from your existing JSON file
    markets = load_markets(MARKETS_JSON_INPUT_FILE)
    print(f"📍 Loaded {len(markets)} markets from {MARKETS_JSON_INPUT_FILE}")

    # 2. Build the travel time matrix (this will use the API)
    print("🕒 Building travel time matrix...")
    matrix = build_travel_time_matrix(markets)

    # 3. Save the new matrix
    save_travel_times(matrix, TRAVEL_TIMES_OUTPUT_FILE)
    print(f"✅ Travel times saved to {TRAVEL_TIMES_OUTPUT_FILE}")

if __name__ == "__main__":
    main()