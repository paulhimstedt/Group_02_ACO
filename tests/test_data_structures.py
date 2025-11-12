"""
Basic tests for data structures
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import time
from src.models.data_structures import Market, Solution, ProblemInstance


def test_market_creation():
    """Test market object creation"""
    market = Market(
        id=1,
        name="Test Market",
        latitude=48.2108,
        longitude=16.3570,
        opening_time=time(10, 0),
        closing_time=time(22, 0),
        description="Test description"
    )
    
    assert market.id == 1
    assert market.name == "Test Market"
    assert market.is_open_at(time(15, 0)) == True
    assert market.is_open_at(time(9, 0)) == False


def test_market_latest_arrival():
    """Test latest arrival time calculation"""
    market = Market(
        id=1,
        name="Test Market",
        latitude=48.2108,
        longitude=16.3570,
        opening_time=time(10, 0),
        closing_time=time(20, 0)
    )
    
    latest = market.latest_arrival_time(30)  # 30 min stay
    assert latest == time(19, 30)


def test_solution_creation():
    """Test solution object creation"""
    solution = Solution(
        route=[1, 2, 3],
        arrival_times=[time(10, 0), time(11, 0), time(12, 0)],
        total_markets_visited=3,
        total_travel_time=45.0,
        total_time=135.0,
        is_feasible=True,
        day=1
    )
    
    assert len(solution.route) == 3
    assert solution.total_markets_visited == 3
    assert solution.is_feasible == True


def test_problem_instance():
    """Test problem instance creation"""
    markets = [
        Market(1, "M1", 48.2, 16.3, time(10, 0), time(20, 0)),
        Market(2, "M2", 48.3, 16.4, time(11, 0), time(21, 0))
    ]
    
    travel_times = {
        (1, 2): 15.0,
        (2, 1): 15.0
    }
    
    problem = ProblemInstance(
        markets=markets,
        travel_times=travel_times,
        num_days=1,
        stay_durations=[30]
    )
    
    assert len(problem.markets) == 2
    assert problem.get_travel_time(1, 2) == 15.0
    assert problem.get_earliest_opening() == time(10, 0)
    assert problem.get_latest_closing() == time(21, 0)


if __name__ == "__main__":
    test_market_creation()
    test_market_latest_arrival()
    test_solution_creation()
    test_problem_instance()
    print("✓ All basic tests passed!")
