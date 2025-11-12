"""
Visualization utilities for the Christmas Market optimizer.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict
from datetime import time, datetime
import os

from ..models.data_structures import Solution, ProblemInstance, MultiDaySolution


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class Visualizer:
    """Visualization tool for solutions."""
    
    def __init__(self, problem: ProblemInstance, output_dir: str = "results"):
        """Initialize visualizer."""
        self.problem = problem
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_route_map(self, solution: Solution, save: bool = True, filename: str = "route_map.png"):
        """Plot the route on a map with market locations."""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Plot all markets
        all_lats = [m.latitude for m in self.problem.markets]
        all_lons = [m.longitude for m in self.problem.markets]
        
        ax.scatter(all_lons, all_lats, c='lightgray', s=100, alpha=0.5, 
                  label='Unvisited Markets', zorder=1)
        
        # Plot visited markets
        if solution.route:
            visited_markets = [self.problem.get_market_by_id(mid) for mid in solution.route]
            visited_lats = [m.latitude for m in visited_markets]
            visited_lons = [m.longitude for m in visited_markets]
            
            # Color by visit order
            colors = plt.cm.viridis(np.linspace(0, 1, len(visited_markets)))
            
            ax.scatter(visited_lons, visited_lats, c=colors, s=300, 
                      edgecolors='black', linewidths=2, zorder=3, label='Visited Markets')
            
            # Plot route lines
            for i in range(len(visited_markets) - 1):
                ax.plot([visited_lons[i], visited_lons[i+1]], 
                       [visited_lats[i], visited_lats[i+1]],
                       'b-', alpha=0.6, linewidth=2, zorder=2)
                
                # Add arrow
                dx = visited_lons[i+1] - visited_lons[i]
                dy = visited_lats[i+1] - visited_lats[i]
                ax.arrow(visited_lons[i], visited_lats[i], dx*0.8, dy*0.8,
                        head_width=0.001, head_length=0.001, fc='blue', 
                        ec='blue', alpha=0.5, zorder=2)
            
            # Add market numbers
            for i, (lon, lat, market) in enumerate(zip(visited_lons, visited_lats, visited_markets)):
                ax.annotate(f"{i+1}", (lon, lat), fontsize=10, fontweight='bold',
                           ha='center', va='center', color='white', zorder=4)
        
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title(f'Christmas Market Route - Day {solution.day}\n'
                    f'{solution.total_markets_visited} markets visited', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved route map to {filepath}")
        
        return fig, ax
    
    def plot_gantt_chart(self, solution: Solution, save: bool = True, filename: str = "gantt.png"):
        """Plot Gantt chart showing market visits over time."""
        if not solution.route:
            print("No route to visualize")
            return None, None
        
        fig, ax = plt.subplots(figsize=(14, max(8, len(solution.route) * 0.5)))
        
        stay_duration = self.problem.stay_durations[solution.day - 1]
        
        for i, (market_id, arrival_time) in enumerate(zip(solution.route, solution.arrival_times)):
            market = self.problem.get_market_by_id(market_id)
            
            # Convert times to minutes
            arrival_min = arrival_time.hour * 60 + arrival_time.minute
            departure_min = arrival_min + stay_duration
            
            opening_min = market.opening_time.hour * 60 + market.opening_time.minute
            closing_min = market.closing_time.hour * 60 + market.closing_time.minute
            
            # Plot market opening hours
            ax.barh(i, closing_min - opening_min, left=opening_min, height=0.8,
                   color='lightgray', alpha=0.5, edgecolor='black', linewidth=1)
            
            # Plot visit time
            ax.barh(i, stay_duration, left=arrival_min, height=0.8,
                   color='green', alpha=0.7, edgecolor='darkgreen', linewidth=2)
            
            # Add travel time if not first market
            if i > 0:
                prev_market_id = solution.route[i-1]
                prev_arrival = solution.arrival_times[i-1]
                prev_departure = prev_arrival.hour * 60 + prev_arrival.minute + stay_duration
                
                ax.barh(i, arrival_min - prev_departure, left=prev_departure, height=0.3,
                       color='orange', alpha=0.6, label='Travel' if i == 1 else '')
        
        # Set labels
        market_names = [self.problem.get_market_by_id(mid).name for mid in solution.route]
        ax.set_yticks(range(len(solution.route)))
        ax.set_yticklabels([f"{i+1}. {name}" for i, name in enumerate(market_names)], fontsize=10)
        
        # Format x-axis as time
        hour_ticks = list(range(10, 23))
        ax.set_xticks([h * 60 for h in hour_ticks])
        ax.set_xticklabels([f"{h}:00" for h in hour_ticks])
        
        ax.set_xlabel('Time of Day', fontsize=12)
        ax.set_ylabel('Markets (in visit order)', fontsize=12)
        ax.set_title(f'Market Visit Schedule - Day {solution.day}', fontsize=14, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='lightgray', edgecolor='black', label='Market Open Hours'),
            Patch(facecolor='green', edgecolor='darkgreen', label='Visit Time'),
            Patch(facecolor='orange', label='Travel Time')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved Gantt chart to {filepath}")
        
        return fig, ax
    
    def plot_convergence(self, convergence_history: List[int], save: bool = True, 
                        filename: str = "convergence.png"):
        """Plot algorithm convergence."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(convergence_history, linewidth=2, color='blue')
        ax.fill_between(range(len(convergence_history)), convergence_history, 
                        alpha=0.3, color='blue')
        
        ax.set_xlabel('Iteration', fontsize=12)
        ax.set_ylabel('Number of Markets Visited', fontsize=12)
        ax.set_title('Algorithm Convergence', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add best value annotation
        best_val = max(convergence_history)
        best_iter = convergence_history.index(best_val)
        ax.annotate(f'Best: {best_val} markets\n(iteration {best_iter})',
                   xy=(best_iter, best_val), xytext=(10, 10),
                   textcoords='offset points', fontsize=11,
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved convergence plot to {filepath}")
        
        return fig, ax
    
    def plot_statistics(self, solution: Solution, save: bool = True, 
                       filename: str = "statistics.png"):
        """Plot solution statistics."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        if not solution.route:
            fig.suptitle("No feasible solution found", fontsize=16, fontweight='bold')
            return fig, (ax1, ax2, ax3, ax4)
        
        # 1. Markets visited vs total
        visited = solution.total_markets_visited
        total = len(self.problem.markets)
        ax1.bar(['Visited', 'Unvisited'], [visited, total - visited], 
               color=['green', 'red'], alpha=0.7)
        ax1.set_ylabel('Number of Markets', fontsize=11)
        ax1.set_title(f'Market Coverage: {visited}/{total} ({100*visited/total:.1f}%)', 
                     fontsize=12, fontweight='bold')
        ax1.grid(True, axis='y', alpha=0.3)
        
        # 2. Time breakdown
        stay_duration = self.problem.stay_durations[solution.day - 1]
        total_stay = visited * stay_duration
        travel_time = solution.total_travel_time
        
        ax2.pie([total_stay, travel_time], labels=['Visiting Markets', 'Traveling'],
               autopct='%1.1f%%', colors=['green', 'orange'], startangle=90)
        ax2.set_title(f'Time Distribution\nTotal: {solution.total_time:.0f} min', 
                     fontsize=12, fontweight='bold')
        
        # 3. Travel distances between consecutive markets
        if len(solution.route) > 1:
            distances = [self.problem.get_travel_time(solution.route[i], solution.route[i+1])
                        for i in range(len(solution.route) - 1)]
            ax3.plot(range(1, len(distances) + 1), distances, 'o-', linewidth=2, markersize=8)
            ax3.set_xlabel('Segment', fontsize=11)
            ax3.set_ylabel('Travel Time (min)', fontsize=11)
            ax3.set_title(f'Travel Times Between Markets\nAvg: {np.mean(distances):.1f} min', 
                         fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # 4. Market opening hours distribution
        visited_markets = [self.problem.get_market_by_id(mid) for mid in solution.route]
        opening_hours = [m.opening_time.hour + m.opening_time.minute/60 for m in visited_markets]
        closing_hours = [m.closing_time.hour + m.closing_time.minute/60 for m in visited_markets]
        
        x_pos = np.arange(len(visited_markets))
        ax4.barh(x_pos, [c - o for o, c in zip(opening_hours, closing_hours)], 
                left=opening_hours, alpha=0.7, color='skyblue')
        ax4.set_yticks(x_pos)
        ax4.set_yticklabels([f"M{i+1}" for i in range(len(visited_markets))], fontsize=9)
        ax4.set_xlabel('Hour of Day', fontsize=11)
        ax4.set_title('Market Opening Hours', fontsize=12, fontweight='bold')
        ax4.grid(True, axis='x', alpha=0.3)
        
        fig.suptitle(f'Solution Statistics - Day {solution.day}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved statistics plot to {filepath}")
        
        return fig, (ax1, ax2, ax3, ax4)
    
    def plot_multi_day_summary(self, multi_solution: MultiDaySolution, save: bool = True,
                              filename: str = "multi_day_summary.png"):
        """Plot summary of multi-day solution."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Markets visited per day
        markets_per_day = [sol.total_markets_visited for sol in multi_solution.daily_solutions]
        days = [f"Day {sol.day}" for sol in multi_solution.daily_solutions]
        
        ax1.bar(days, markets_per_day, color='steelblue', alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Markets Visited', fontsize=12)
        ax1.set_title('Markets Visited Per Day', fontsize=13, fontweight='bold')
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(markets_per_day):
            ax1.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
        
        # Cumulative progress
        cumulative = np.cumsum(markets_per_day)
        total_markets = len(self.problem.markets)
        
        ax2.plot(range(1, len(cumulative) + 1), cumulative, 'o-', linewidth=2, 
                markersize=10, color='green', label='Visited')
        ax2.axhline(y=total_markets, color='red', linestyle='--', 
                   linewidth=2, label=f'Total ({total_markets})')
        ax2.fill_between(range(1, len(cumulative) + 1), cumulative, alpha=0.3, color='green')
        
        ax2.set_xlabel('Day', fontsize=12)
        ax2.set_ylabel('Cumulative Markets Visited', fontsize=12)
        ax2.set_title('Cumulative Progress', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(f'Multi-Day Solution Summary\n'
                    f'Total: {multi_solution.total_markets_visited}/{total_markets} markets '
                    f'({100*multi_solution.total_markets_visited/total_markets:.1f}%)',
                    fontsize=15, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved multi-day summary to {filepath}")
        
        return fig, (ax1, ax2)
    
    def create_solution_report(self, solution: Solution):
        """Print text report of solution."""
        print("\n" + "="*70)
        print(f"SOLUTION REPORT - DAY {solution.day}")
        print("="*70)
        
        if not solution.is_feasible or not solution.route:
            print("No feasible solution found!")
            return
        
        print(f"\nMarkets Visited: {solution.total_markets_visited}/{len(self.problem.markets)}")
        print(f"Total Travel Time: {solution.total_travel_time:.1f} minutes")
        print(f"Total Time: {solution.total_time:.1f} minutes")
        
        stay_duration = self.problem.stay_durations[solution.day - 1]
        
        print(f"\nDetailed Route:")
        print("-" * 70)
        for i, (market_id, arrival) in enumerate(zip(solution.route, solution.arrival_times)):
            market = self.problem.get_market_by_id(market_id)
            departure_time = datetime.combine(datetime.today(), arrival) + \
                           __import__('datetime').timedelta(minutes=stay_duration)
            
            travel_info = ""
            if i > 0:
                prev_id = solution.route[i-1]
                travel = self.problem.get_travel_time(prev_id, market_id)
                travel_info = f" (travel: {travel:.0f} min)"
            
            print(f"{i+1}. {market.name}")
            print(f"   Arrive: {arrival.strftime('%H:%M')} | "
                  f"Depart: {departure_time.strftime('%H:%M')} | "
                  f"Open: {market.opening_time.strftime('%H:%M')}-{market.closing_time.strftime('%H:%M')}"
                  f"{travel_info}")
        
        print("="*70 + "\n")
