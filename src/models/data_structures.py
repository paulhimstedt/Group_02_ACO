"""
Data structures for the Christmas Market optimization problem.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time, datetime, timedelta
import json


@dataclass
class Market:
    """Represents a Christmas market with its constraints."""
    id: int
    name: str
    latitude: float
    longitude: float
    opening_time: time
    closing_time: time
    description: str = ""
    
    def is_open_at(self, current_time: time) -> bool:
        """Check if market is open at given time."""
        return self.opening_time <= current_time <= self.closing_time
    
    def latest_arrival_time(self, stay_duration_minutes: int) -> time:
        """Calculate latest arrival time given stay duration."""
        closing_datetime = datetime.combine(datetime.today(), self.closing_time)
        latest_datetime = closing_datetime - timedelta(minutes=stay_duration_minutes)
        return latest_datetime.time()
    
    def __repr__(self):
        return f"Market({self.id}: {self.name})"


@dataclass
class Solution:
    """Represents a solution to the optimization problem."""
    route: List[int]  # List of market IDs in visit order
    arrival_times: List[time]  # Arrival time at each market
    total_markets_visited: int
    total_travel_time: float  # in minutes
    total_time: float  # in minutes (including stay duration)
    is_feasible: bool
    day: int = 1
    
    def __repr__(self):
        return (f"Solution(markets={self.total_markets_visited}, "
                f"travel_time={self.total_travel_time:.1f}min, "
                f"feasible={self.is_feasible})")


@dataclass
class MultiDaySolution:
    """Represents a multi-day solution."""
    daily_solutions: List[Solution]
    total_markets_visited: int
    unvisited_markets: List[int]
    
    def __repr__(self):
        return (f"MultiDaySolution({len(self.daily_solutions)} days, "
                f"{self.total_markets_visited} markets)")


@dataclass
class ProblemInstance:
    """Contains all data for the optimization problem."""
    markets: List[Market]
    travel_times: Dict[tuple, float]  # (from_id, to_id) -> time in minutes
    num_days: int
    stay_durations: List[int]  # Stay duration per day
    transfer_buffer: int = 5  # Buffer time for transfers
    
    def get_travel_time(self, from_id: int, to_id: int) -> float:
        """Get travel time between two markets."""
        if from_id == to_id:
            return 0.0
        return self.travel_times.get((from_id, to_id), 
                                     self.travel_times.get((to_id, from_id), float('inf')))
    
    def get_market_by_id(self, market_id: int) -> Optional[Market]:
        """Get market by ID."""
        for market in self.markets:
            if market.id == market_id:
                return market
        return None
    
    def get_earliest_opening(self) -> time:
        """Get earliest opening time across all markets."""
        return min(m.opening_time for m in self.markets)
    
    def get_latest_closing(self) -> time:
        """Get latest closing time across all markets."""
        return max(m.closing_time for m in self.markets)
    
    def get_day_bounds(self) -> tuple:
        """Get (start_time, end_time) for a day."""
        return self.get_earliest_opening(), self.get_latest_closing()


def load_problem_instance(markets_path: str, 
                          travel_times_path: str,
                          num_days: int = 1,
                          stay_durations: List[int] = None,
                          transfer_buffer: int = 5) -> ProblemInstance:
    """Load problem instance from JSON files."""
    
    # Load markets
    with open(markets_path, 'r') as f:
        markets_data = json.load(f)
    
    markets = []
    for m in markets_data:
        opening = datetime.strptime(m['opening_time'], '%H:%M').time()
        closing = datetime.strptime(m['closing_time'], '%H:%M').time()
        markets.append(Market(
            id=int(m['id']),  # Convert to int to match travel_times keys
            name=m['name'],
            latitude=m['latitude'],
            longitude=m['longitude'],
            opening_time=opening,
            closing_time=closing,
            description=m.get('description', '')
        ))
    
    # Load travel times
    with open(travel_times_path, 'r') as f:
        travel_data = json.load(f)
    
    travel_times = {}
    for from_id, destinations in travel_data['times'].items():
        for to_id, time_minutes in destinations.items():
            travel_times[(int(from_id), int(to_id))] = float(time_minutes)
    
    # Set default stay durations
    if stay_durations is None:
        stay_durations = [30] * num_days
    elif len(stay_durations) < num_days:
        # Extend with last value
        stay_durations = stay_durations + [stay_durations[-1]] * (num_days - len(stay_durations))
    
    return ProblemInstance(
        markets=markets,
        travel_times=travel_times,
        num_days=num_days,
        stay_durations=stay_durations,
        transfer_buffer=transfer_buffer
    )
