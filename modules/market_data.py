# modules/market_data.py

import json
from datetime import datetime
import csv

class Market:
    def __init__(self, id_, name, open_time, close_time, lat=None, lon=None, url=None):
        self.id = str(id_)
        self.name = name
        self.latitude = lat
        self.longitude = lon
        self.opening_time = self._parse_time(open_time)
        self.closing_time = self._parse_time(close_time)
        self.url = url

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
            open_time=item["opening_time"],
            close_time=item["closing_time"],
            lat=item["latitude"],
            lon=item["longitude"]
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

def load_markets_from_csv(filepath):
    """Load market information from CSV."""
    markets = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row: # skip empty rows
                continue
            # CSV format: Name,URL,OpenTime,CloseTime
            market = Market(
                id_=i + 1,       # Auto-generate ID
                name=row[0],
                open_time=row[2],
                close_time=row[3],
                url=row[1]       # Pass the URL
            )
            markets.append(market)
    return markets