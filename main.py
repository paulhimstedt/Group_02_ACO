# main.py

from modules.market_data import load_markets
from modules.travel_times import build_travel_time_matrix, save_travel_times

def main():
    markets = load_markets("data/real/markets.json")
    print(f"📍 Loaded {len(markets)} markets")

    print("🕒 Building travel time matrix...")
    matrix = build_travel_time_matrix(markets)

    save_travel_times(matrix, "data/real/travel_times.json")
    print("✅ Travel times saved to data/real/travel_times.json")

if __name__ == "__main__":
    main()
