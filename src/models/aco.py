"""
Ant Colony Optimization for the Christmas Market routing problem.
"""
import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta, time
import logging
from ..models.data_structures import ProblemInstance, Solution


logger = logging.getLogger(__name__)


class AntColonyOptimizer:
    """ACO algorithm for time-constrained market visiting."""
    
    def __init__(self,
                 problem: ProblemInstance,
                 num_ants: int = 50,
                 num_iterations: int = 100,
                 alpha: float = 1.0,
                 beta: float = 2.0,
                 gamma: float = 1.5,
                 evaporation: float = 0.5,
                 pheromone_init: float = 1.0,
                 Q: float = 100.0,
                 use_elite: bool = True,
                 elite_weight: float = 2.0,
                 random_seed: int = 42):
        """
        Initialize ACO optimizer.
        
        Args:
            problem: ProblemInstance to solve
            num_ants: Number of ants per iteration
            num_iterations: Number of iterations
            alpha: Pheromone importance factor
            beta: Heuristic (distance) importance factor
            gamma: Time window urgency importance factor
            evaporation: Pheromone evaporation rate (0-1)
            pheromone_init: Initial pheromone level
            Q: Pheromone deposit constant
            use_elite: Use elite ant strategy
            elite_weight: Weight for elite ant pheromone
            random_seed: Random seed for reproducibility
        """
        self.problem = problem
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.evaporation = evaporation
        self.Q = Q
        self.use_elite = use_elite
        self.elite_weight = elite_weight
        
        np.random.seed(random_seed)
        
        # Initialize pheromone matrix
        n = len(problem.markets)
        self.pheromones = np.ones((n, n)) * pheromone_init
        
        # Best solution tracking
        self.best_solution = None
        self.convergence_history = []
        
    def solve(self, day: int = 1, excluded_markets: List[int] = None) -> Solution:
        """
        Run ACO algorithm.
        
        Args:
            day: Which day we're solving for (affects stay duration)
            excluded_markets: Markets already visited on previous days
            
        Returns:
            Best solution found
        """
        if excluded_markets is None:
            excluded_markets = []
        
        stay_duration = self.problem.stay_durations[day - 1]
        
        logger.info(f"Starting ACO for day {day} with {self.num_iterations} iterations")
        
        for iteration in range(self.num_iterations):
            solutions = []
            
            # Each ant constructs a solution
            for ant in range(self.num_ants):
                solution = self._construct_solution(stay_duration, excluded_markets)
                solutions.append(solution)
            
            # Update best solution
            feasible_solutions = [s for s in solutions if s.is_feasible]
            if feasible_solutions:
                iteration_best = max(feasible_solutions, 
                                   key=lambda s: s.total_markets_visited)
                
                if (self.best_solution is None or 
                    iteration_best.total_markets_visited > self.best_solution.total_markets_visited):
                    self.best_solution = iteration_best
                    logger.debug(f"Iteration {iteration}: New best with {iteration_best.total_markets_visited} markets")
            
            # Track convergence
            if self.best_solution:
                self.convergence_history.append(self.best_solution.total_markets_visited)
            else:
                self.convergence_history.append(0)
            
            # Update pheromones
            self._update_pheromones(solutions)
            
            if (iteration + 1) % 10 == 0:
                best_count = self.best_solution.total_markets_visited if self.best_solution else 0
                logger.info(f"Iteration {iteration + 1}/{self.num_iterations}: Best = {best_count} markets")
        
        if self.best_solution:
            self.best_solution.day = day
            logger.info(f"ACO completed: Best solution visits {self.best_solution.total_markets_visited} markets")
        else:
            logger.warning("No feasible solution found!")
            # Return empty solution
            self.best_solution = Solution(
                route=[], arrival_times=[], total_markets_visited=0,
                total_travel_time=0, total_time=0, is_feasible=False, day=day
            )
        
        return self.best_solution
    
    def _construct_solution(self, stay_duration: int, excluded_markets: List[int]) -> Solution:
        """Construct a solution using ACO probabilistic selection."""
        available_markets = [m.id for m in self.problem.markets if m.id not in excluded_markets]
        
        if not available_markets:
            return Solution([], [], 0, 0, 0, False)
        
        # Start at random available market
        current_id = np.random.choice(available_markets)
        route = [current_id]
        visited = {current_id}
        
        # Start time is when market opens
        current_market = self.problem.get_market_by_id(current_id)
        current_time = self._time_to_minutes(current_market.opening_time)
        arrival_times = [self._minutes_to_time(current_time)]
        
        # Visit markets until no more can be added
        while True:
            next_id = self._select_next_market(current_id, visited, current_time, 
                                               stay_duration, excluded_markets)
            if next_id is None:
                break
            
            # Calculate arrival time at next market
            travel_time = self.problem.get_travel_time(current_id, next_id)
            current_time += stay_duration + travel_time + self.problem.transfer_buffer
            
            next_market = self.problem.get_market_by_id(next_id)
            arrival_time_minutes = current_time
            
            # Check if we can visit (must arrive before latest allowed time)
            latest_arrival = self._time_to_minutes(next_market.latest_arrival_time(stay_duration))
            
            if arrival_time_minutes > latest_arrival:
                break
            
            # Ensure we arrive after opening
            opening_minutes = self._time_to_minutes(next_market.opening_time)
            if arrival_time_minutes < opening_minutes:
                current_time = opening_minutes
                arrival_time_minutes = opening_minutes
            
            route.append(next_id)
            visited.add(next_id)
            arrival_times.append(self._minutes_to_time(arrival_time_minutes))
            current_id = next_id
        
        # Calculate solution metrics
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
                           stay_duration: int, excluded_markets: List[int]) -> int:
        """Select next market using ACO probability."""
        available = [m for m in self.problem.markets 
                    if m.id not in visited and m.id not in excluded_markets]
        
        if not available:
            return None
        
        probabilities = []
        market_ids = []
        
        current_idx = self._get_market_index(current_id)
        
        for market in available:
            market_idx = self._get_market_index(market.id)
            
            # Pheromone component
            pheromone = self.pheromones[current_idx, market_idx]
            
            # Heuristic component (inverse of distance)
            distance = self.problem.get_travel_time(current_id, market.id)
            if distance == 0:
                distance = 0.01
            heuristic = 1.0 / distance
            
            # Time window urgency (prefer markets closing soon)
            time_after_travel = current_time + stay_duration + distance + self.problem.transfer_buffer
            closing_minutes = self._time_to_minutes(market.closing_time)
            time_until_close = closing_minutes - time_after_travel
            
            if time_until_close < stay_duration:
                # Can't visit this market
                continue
            
            urgency = 1.0 / max(time_until_close, 1.0)
            
            # Combined probability
            prob = (pheromone ** self.alpha) * (heuristic ** self.beta) * (urgency ** self.gamma)
            probabilities.append(prob)
            market_ids.append(market.id)
        
        if not probabilities:
            return None
        
        # Normalize probabilities
        probabilities = np.array(probabilities)
        probabilities = probabilities / probabilities.sum()
        
        # Select market
        selected_id = np.random.choice(market_ids, p=probabilities)
        return selected_id
    
    def _update_pheromones(self, solutions: List[Solution]):
        """Update pheromone matrix based on solutions."""
        # Evaporation
        self.pheromones *= (1 - self.evaporation)
        
        # Deposit pheromones
        for solution in solutions:
            if not solution.is_feasible or len(solution.route) < 2:
                continue
            
            # Pheromone amount proportional to number of markets visited
            deposit = self.Q * solution.total_markets_visited / len(self.problem.markets)
            
            for i in range(len(solution.route) - 1):
                from_idx = self._get_market_index(solution.route[i])
                to_idx = self._get_market_index(solution.route[i + 1])
                self.pheromones[from_idx, to_idx] += deposit
        
        # Elite ant strategy
        if self.use_elite and self.best_solution and len(self.best_solution.route) > 1:
            elite_deposit = self.Q * self.best_solution.total_markets_visited * self.elite_weight
            elite_deposit /= len(self.problem.markets)
            
            for i in range(len(self.best_solution.route) - 1):
                from_idx = self._get_market_index(self.best_solution.route[i])
                to_idx = self._get_market_index(self.best_solution.route[i + 1])
                self.pheromones[from_idx, to_idx] += elite_deposit
    
    def _get_market_index(self, market_id: int) -> int:
        """Get array index for market ID."""
        for i, m in enumerate(self.problem.markets):
            if m.id == market_id:
                return i
        return 0
    
    def _time_to_minutes(self, t: time) -> float:
        """Convert time to minutes since midnight."""
        return t.hour * 60 + t.minute
    
    def _minutes_to_time(self, minutes: float) -> time:
        """Convert minutes since midnight to time."""
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return time(hour=hours % 24, minute=mins)
