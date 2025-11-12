"""
Main entry point for the Vienna Christmas Market Optimizer.
"""
import argparse
import yaml
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.data_structures import load_problem_instance, MultiDaySolution
from src.models.aco import AntColonyOptimizer
from src.models.greedy import GreedyOptimizer
from src.visualization.plotter import Visualizer


def setup_logging(level: str):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def solve_single_day(problem, algorithm, config, day=1, excluded_markets=None):
    """Solve for a single day."""
    if excluded_markets is None:
        excluded_markets = []
    
    algo_type = config['algorithm']['type']
    
    if algo_type == 'aco':
        optimizer = AntColonyOptimizer(
            problem=problem,
            num_ants=config['aco']['num_ants'],
            num_iterations=config['aco']['num_iterations'],
            alpha=config['aco']['alpha'],
            beta=config['aco']['beta'],
            gamma=config['aco']['gamma'],
            evaporation=config['aco']['evaporation'],
            pheromone_init=config['aco']['pheromone_init'],
            Q=config['aco']['Q'],
            use_elite=config['aco']['use_elite'],
            elite_weight=config['aco']['elite_weight'],
            random_seed=config['performance']['random_seed']
        )
        solution = optimizer.solve(day=day, excluded_markets=excluded_markets)
        convergence = optimizer.convergence_history
    elif algo_type == 'greedy':
        optimizer = GreedyOptimizer(
            problem=problem,
            heuristic=config['greedy']['heuristic'],
            distance_weight=config['greedy']['distance_weight'],
            time_window_weight=config['greedy']['time_window_weight']
        )
        solution = optimizer.solve(day=day, excluded_markets=excluded_markets)
        convergence = None
    else:
        raise ValueError(f"Unknown algorithm type: {algo_type}")
    
    return solution, convergence


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Vienna Christmas Market Route Optimizer'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/default.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading configuration from {args.config}")
    config = load_config(args.config)
    
    # Setup logging
    setup_logging(config['output']['log_level'])
    logger = logging.getLogger(__name__)
    
    # Load data
    if config['data']['use_demo']:
        markets_path = config['data']['demo_markets_path']
        travel_times_path = config['data']['demo_travel_times_path']
        logger.info("Using demo data")
    else:
        markets_path = config['data']['real_markets_path']
        travel_times_path = config['data']['real_travel_times_path']
        logger.info("Using real data")
    
    # Load problem instance
    logger.info("Loading problem instance...")
    problem = load_problem_instance(
        markets_path=markets_path,
        travel_times_path=travel_times_path,
        num_days=config['problem']['num_days'],
        stay_durations=config['problem']['stay_duration'],
        transfer_buffer=config['problem']['transfer_buffer']
    )
    
    logger.info(f"Loaded {len(problem.markets)} markets")
    logger.info(f"Solving for {problem.num_days} day(s)")
    
    # Create output directory
    output_dir = config['output']['results_dir']
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize visualizer
    visualizer = Visualizer(problem, output_dir)
    
    # Solve
    excluded_markets = []
    daily_solutions = []
    all_convergence = []
    
    for day in range(1, problem.num_days + 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"SOLVING DAY {day}")
        logger.info(f"{'='*60}")
        logger.info(f"Stay duration: {problem.stay_durations[day-1]} minutes")
        logger.info(f"Remaining markets: {len(problem.markets) - len(excluded_markets)}")
        
        solution, convergence = solve_single_day(
            problem, config['algorithm']['type'], config, 
            day=day, excluded_markets=excluded_markets
        )
        
        daily_solutions.append(solution)
        if convergence:
            all_convergence.append(convergence)
        
        # Update excluded markets
        excluded_markets.extend(solution.route)
        
        # Visualize day solution
        if config['output']['verbose']:
            visualizer.create_solution_report(solution)
        
        if config['visualization']['plot_route']:
            visualizer.plot_route_map(
                solution, 
                save=config['visualization']['save_figures'],
                filename=f"day{day}_route_map.{config['visualization']['figure_format']}"
            )
        
        if config['visualization']['plot_gantt']:
            visualizer.plot_gantt_chart(
                solution,
                save=config['visualization']['save_figures'],
                filename=f"day{day}_gantt.{config['visualization']['figure_format']}"
            )
        
        if config['visualization']['plot_statistics']:
            visualizer.plot_statistics(
                solution,
                save=config['visualization']['save_figures'],
                filename=f"day{day}_statistics.{config['visualization']['figure_format']}"
            )
        
        if convergence and config['visualization']['plot_convergence']:
            visualizer.plot_convergence(
                convergence,
                save=config['visualization']['save_figures'],
                filename=f"day{day}_convergence.{config['visualization']['figure_format']}"
            )
    
    # Multi-day summary
    total_visited = sum(s.total_markets_visited for s in daily_solutions)
    unvisited = [m.id for m in problem.markets if m.id not in excluded_markets]
    
    multi_solution = MultiDaySolution(
        daily_solutions=daily_solutions,
        total_markets_visited=total_visited,
        unvisited_markets=unvisited
    )
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Total markets visited: {total_visited}/{len(problem.markets)} "
          f"({100*total_visited/len(problem.markets):.1f}%)")
    print(f"Unvisited markets: {len(unvisited)}")
    
    for i, sol in enumerate(daily_solutions):
        print(f"  Day {i+1}: {sol.total_markets_visited} markets, "
              f"{sol.total_time:.1f} min total time")
    
    if len(daily_solutions) > 1:
        visualizer.plot_multi_day_summary(
            multi_solution,
            save=config['visualization']['save_figures'],
            filename=f"multi_day_summary.{config['visualization']['figure_format']}"
        )
    
    print(f"\nResults saved to: {output_dir}/")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
