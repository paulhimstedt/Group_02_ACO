# modules/market_data.py

import json
from datetime import datetime

class Market:
    def __init__(self, id_, name, lat, lon, open_time, close_time):
        self.id = str(id_)  # IDs als Strings!
        self.name = name
        self.latitude = lat
        self.longitude = lon
        self.opening_time = self._parse_time(open_time)
        self.closing_time = self._parse_time(close_time)

    def _parse_time(self, t):
        return datetime.strptime(t, "%H:%M").time()

def load_markets(filepath):
    """Load market information from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    markets = [
        Market(
            id_=item["id"],
            name=item["name"],
            lat=item["latitude"],
            lon=item["longitude"],
            open_time=item["opening_time"],
            close_time=item["closing_time"],
        )
        for item in data
    ]
    return markets

def save_markets(markets, filepath):
    """Save markets back to JSON (useful if coords were added)."""
    data = [
        {
            "id": m.id,
            "name": m.name,
            "latitude": m.latitude,
            "longitude": m.longitude,
            "opening_time": m.opening_time.strftime("%H:%M"),
            "closing_time": m.closing_time.strftime("%H:%M"),
        }
        for m in markets
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
