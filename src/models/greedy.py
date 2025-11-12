"""
Greedy algorithms for the Christmas Market problem.
"""
from typing import List
from datetime import time, datetime, timedelta
import logging
from ..models.data_structures import ProblemInstance, Solution, Market


logger = logging.getLogger(__name__)


class GreedyOptimizer:
    """Greedy heuristic algorithms for market visiting."""
    
    def __init__(self, problem: ProblemInstance, heuristic: str = "hybrid",
                 distance_weight: float = 0.4, time_window_weight: float = 0.6):
        """
        Initialize greedy optimizer.
        
        Args:
            problem: ProblemInstance to solve
            heuristic: Type of heuristic ("nearest", "earliest_closing", "time_efficient", "hybrid")
            distance_weight: Weight for distance in hybrid heuristic
            time_window_weight: Weight for time window in hybrid heuristic
        """
        self.problem = problem
        self.heuristic = heuristic
        self.distance_weight = distance_weight
        self.time_window_weight = time_window_weight
    
    def solve(self, day: int = 1, excluded_markets: List[int] = None) -> Solution:
        """
        Run greedy algorithm.
        
        Args:
            day: Which day we're solving for
            excluded_markets: Markets already visited
            
        Returns:
            Best solution found
        """
        if excluded_markets is None:
            excluded_markets = []
        
        stay_duration = self.problem.stay_durations[day - 1]
        
        # Try starting from each available market
        best_solution = None
        available_starts = [m for m in self.problem.markets if m.id not in excluded_markets]
        
        for start_market in available_starts:
            solution = self._construct_solution(start_market, stay_duration, excluded_markets)
            
            if solution.is_feasible:
                if (best_solution is None or 
                    solution.total_markets_visited > best_solution.total_markets_visited):
                    best_solution = solution
        
        if best_solution:
            best_solution.day = day
            logger.info(f"Greedy ({self.heuristic}) found solution with {best_solution.total_markets_visited} markets")
        else:
            logger.warning("Greedy: No feasible solution found")
            best_solution = Solution([], [], 0, 0, 0, False, day)
        
        return best_solution
    
    def _construct_solution(self, start_market: Market, stay_duration: int,
                           excluded_markets: List[int]) -> Solution:
        """Construct a greedy solution starting from given market."""
        route = [start_market.id]
        visited = {start_market.id}
        
        current_time = self._time_to_minutes(start_market.opening_time)
        arrival_times = [self._minutes_to_time(current_time)]
        current_id = start_market.id
        
        while True:
            next_market = self._select_next_market(current_id, visited, current_time,
                                                   stay_duration, excluded_markets)
            if next_market is None:
                break
            
            travel_time = self.problem.get_travel_time(current_id, next_market.id)
            current_time += stay_duration + travel_time + self.problem.transfer_buffer
            
            latest_arrival = self._time_to_minutes(next_market.latest_arrival_time(stay_duration))
            if current_time > latest_arrival:
                break
            
            opening_minutes = self._time_to_minutes(next_market.opening_time)
            if current_time < opening_minutes:
                current_time = opening_minutes
            
            route.append(next_market.id)
            visited.add(next_market.id)
            arrival_times.append(self._minutes_to_time(current_time))
            current_id = next_market.id
        
        total_travel = sum(self.problem.get_travel_time(route[i], route[i+1])
                          for i in range(len(route)-1))
        total_time = total_travel + len(route) * stay_duration
        
        return Solution(
            route=route,
            arrival_times=arrival_times,
            total_markets_visited=len(route),
            total_travel_time=total_travel,
            total_time=total_time,
            is_feasible=True
        )
    
    def _select_next_market(self, current_id: int, visited: set, current_time: float,
                           stay_duration: int, excluded_markets: List[int]) -> Market:
        """Select next market based on heuristic."""
        available = [m for m in self.problem.markets
                    if m.id not in visited and m.id not in excluded_markets]
        
        if not available:
            return None
        
        if self.heuristic == "nearest":
            return self._select_nearest(current_id, available)
        elif self.heuristic == "earliest_closing":
            return self._select_earliest_closing(current_id, available, current_time, stay_duration)
        elif self.heuristic == "time_efficient":
            return self._select_time_efficient(current_id, available, current_time, stay_duration)
        else:  # hybrid
            return self._select_hybrid(current_id, available, current_time, stay_duration)
    
    def _select_nearest(self, current_id: int, markets: List[Market]) -> Market:
        """Select nearest market."""
        return min(markets, key=lambda m: self.problem.get_travel_time(current_id, m.id))
    
    def _select_earliest_closing(self, current_id: int, markets: List[Market],
                                current_time: float, stay_duration: int) -> Market:
        """Select market that closes earliest."""
        valid_markets = []
        for m in markets:
            travel_time = self.problem.get_travel_time(current_id, m.id)
            arrival = current_time + stay_duration + travel_time + self.problem.transfer_buffer
            latest = self._time_to_minutes(m.latest_arrival_time(stay_duration))
            
            if arrival <= latest:
                valid_markets.append(m)
        
        if not valid_markets:
            return None
        
        return min(valid_markets, key=lambda m: self._time_to_minutes(m.closing_time))
    
    def _select_time_efficient(self, current_id: int, markets: List[Market],
                              current_time: float, stay_duration: int) -> Market:
        """Select market with best time efficiency."""
        best_market = None
        best_score = float('inf')
        
        for m in markets:
            travel_time = self.problem.get_travel_time(current_id, m.id)
            arrival = current_time + stay_duration + travel_time + self.problem.transfer_buffer
            latest = self._time_to_minutes(m.latest_arrival_time(stay_duration))
            
            if arrival <= latest:
                score = travel_time / max(1, self._time_to_minutes(m.closing_time) - arrival)
                if score < best_score:
                    best_score = score
                    best_market = m
        
        return best_market
    
    def _select_hybrid(self, current_id: int, markets: List[Market],
                      current_time: float, stay_duration: int) -> Market:
        """Select market using hybrid heuristic."""
        best_market = None
        best_score = float('inf')
        
        # Find valid markets first
        valid_markets = []
        for m in markets:
            travel_time = self.problem.get_travel_time(current_id, m.id)
            arrival = current_time + stay_duration + travel_time + self.problem.transfer_buffer
            latest = self._time_to_minutes(m.latest_arrival_time(stay_duration))
            
            if arrival <= latest:
                valid_markets.append((m, travel_time, arrival, latest))
        
        if not valid_markets:
            return None
        
        # Get max distance for normalization
        max_dist = max(travel_time for _, travel_time, _, _ in valid_markets)
        
        for m, travel_time, arrival, latest in valid_markets:
            # Normalize distance
            norm_dist = travel_time / max(max_dist, 1)
            
            # Normalize time urgency
            time_until_close = latest - arrival
            
            # Calculate max time among valid markets
            time_windows = [latest2 - arrival for _, _, _, latest2 in valid_markets]
            max_time = max(time_windows) if time_windows else 1
            
            norm_urgency = 1 - (time_until_close / max(max_time, 1))
            
            # Combined score
            score = self.distance_weight * norm_dist + self.time_window_weight * norm_urgency
            
            if score < best_score:
                best_score = score
                best_market = m
        
        return best_market
    
    def _time_to_minutes(self, t: time) -> float:
        """Convert time to minutes since midnight."""
        return t.hour * 60 + t.minute
    
    def _minutes_to_time(self, minutes: float) -> time:
        """Convert minutes since midnight to time."""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return time(hour=hours % 24, minute=mins)
