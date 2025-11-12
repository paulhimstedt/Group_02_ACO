# Vienna Christmas Market Route Optimizer

## Project Overview
This project solves the time-constrained Christmas market visiting problem using Ant Colony Optimization (ACO) and other heuristic approaches. The goal is to maximize the number of markets visited within opening hours constraints across one or multiple days.

## Team Structure
- **Data Preparation & API Integration**: Teammate
- **Modeling & Optimization**: Current focus (this implementation)

## Problem Description
Given a set of Christmas markets in Vienna with:
- Different opening and closing times
- Travel times between markets (walking/public transport)
- Limited visiting time per day
- Required stay duration at each market

Find an optimal route that maximizes the number of markets visited, supporting both single-day and multi-day scenarios.

## Repository Structure
```
.
├── data/                      # Data directory
│   ├── demo/                  # Demo data for development
│   └── real/                  # Real data (32 Vienna Christmas markets)
├── src/                       # Source code
│   ├── models/                # Optimization models (ACO, Greedy)
│   │   ├── aco.py            # Ant Colony Optimizer
│   │   ├── greedy.py         # Greedy heuristics
│   │   └── data_structures.py # Problem & solution structures
│   ├── utils/                 # Helper functions
│   ├── visualization/         # Plotting and visualization tools
│   └── main.py               # Main entry point
├── modules/                   # Data preparation modules
│   ├── market_data.py        # Market data loader
│   └── travel_times.py       # Travel time matrix builder
├── config/                    # Configuration files
│   ├── default.yaml          # Single-day configuration
│   └── multiday.yaml         # Multi-day configuration (3 days)
├── notebooks/                 # Jupyter notebooks for analysis
│   └── analysis.ipynb        # Complete analysis notebook
├── tests/                     # Unit tests
├── results/                   # Output results and figures
└── docs/                      # Documentation
```

## Key Features
- **Multi-Day Planning**: Support for 1-3 day itineraries with different stay durations per day
- **Multiple Algorithms**: ACO with elite ants and Greedy with hybrid heuristics
- **Comprehensive Visualization**: Route maps, Gantt charts, statistics, convergence plots
- **Interactive Maps**: Folium-based interactive maps showing routes on OpenStreetMap
- **Multi-Day Visualizations**: Side-by-side routes, combined Gantt charts, daily statistics
- **Flexible Configuration**: YAML-based configuration for all parameters
- **Real Data**: 32 actual Vienna Christmas markets with real travel times
- **Demo Mode**: Smaller dataset for testing and development

## Installation

### Prerequisites
- Python 3.8+
- Poetry (recommended) or pip

### Using Poetry (Recommended)
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip (Alternative)
```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Single-Day Optimization
```bash
# Using default configuration (1 day, ACO algorithm)
python src/main.py --config config/default.yaml
```

### 2. Multi-Day Optimization
```bash
# Using multi-day configuration (3 days)
python src/main.py --config config/multiday.yaml
```

### 3. Interactive Analysis (Jupyter Notebook)
```bash
# Start Jupyter
jupyter notebook notebooks/analysis.ipynb
```

The notebook includes:
- Problem instance loading
- Market data exploration with coordinate visualization
- ACO and Greedy algorithm comparison
- **Interactive maps** showing routes on OpenStreetMap (using Folium)
- Multi-day scenario analysis (configurable 2-3 days)
- **Comprehensive multi-day visualizations**: side-by-side routes, combined Gantt charts
- **Interactive multi-day map** with color-coded routes per day
- Parameter sensitivity analysis
- Result export

## Configuration

### Main Configuration Files

**`config/default.yaml`** - Single-day setup
- 1 day planning
- 30 minutes stay duration
- ACO with 50 ants, 100 iterations

**`config/multiday.yaml`** - Multi-day setup
- 3 days planning
- Progressive stay durations: [30, 45, 60] minutes
- Optimized for covering all markets

### Key Parameters
```yaml
problem:
  num_days: 3                    # Number of days (1-3)
  stay_duration: [30, 45, 60]    # Minutes per market (list for multi-day)
  transfer_buffer: 5             # Extra minutes for transfers

algorithm:
  type: "aco"                    # "aco" or "greedy"

aco:
  num_ants: 50                   # Colony size
  num_iterations: 100            # Number of iterations
  alpha: 1.0                     # Pheromone importance
  beta: 2.0                      # Distance heuristic
  gamma: 1.5                     # Time window urgency

visualization:
  plot_route: true               # Route maps
  plot_gantt: true               # Timeline charts
  plot_statistics: true          # Statistics
  plot_convergence: true         # Convergence history
  save_figures: true             # Save to results/
```

## Data Preparation

The project uses real data for Vienna Christmas markets:

### Generate Travel Times
```bash
# Build travel time matrix using routing API
python main.py
```

This creates `data/real/travel_times.json` with walking/transit times between all market pairs.

## Output

Results are saved to `results/` directory:

**Static Visualizations (PNG/PDF):**
- Route maps (showing visited markets and paths)
- Gantt charts (timeline visualization)
- Statistics (markets visited, time utilization)
- Convergence plots (algorithm performance)
- Multi-day summary (for multi-day scenarios)
- Side-by-side route comparison (multi-day)
- Combined multi-day Gantt chart

**Interactive Maps (HTML):**
- Single-day interactive map with clickable markers
- Multi-day interactive map with color-coded routes per day
- Built with Folium on OpenStreetMap tiles
- Popup details showing arrival/departure times and market info

## Algorithms

### Ant Colony Optimization (ACO)
- Elite ant strategy for better solutions
- Time window urgency heuristic
- Pheromone trail evaporation
- Configurable exploration vs exploitation

### Greedy Heuristics
- Nearest neighbor
- Earliest closing time
- Time-efficient (distance/time ratio)
- Hybrid (weighted combination)

## Multi-Day Execution

The system supports multi-day planning where:
1. Each day is solved sequentially
2. Visited markets are excluded from subsequent days
3. Different stay durations can be configured per day
4. Results are aggregated for overall coverage

Example: 3-day configuration visits markets with increasing stay times (30→45→60 min) to simulate realistic visitor behavior.

## Visualization Options

### Static Visualizations (Matplotlib)
All visualizations can be saved as PNG, PDF, or SVG files:

**Single-Day:**
- `plot_route_map()` - Geographic route with numbered waypoints
- `plot_gantt_chart()` - Timeline showing visits and travel times
- `plot_statistics()` - 4-panel dashboard with coverage, time distribution, travel distances
- `plot_convergence()` - Algorithm performance over iterations

**Multi-Day:**
- `plot_multi_day_summary()` - Bar charts showing markets per day and cumulative progress
- `plot_multi_day_routes()` - Side-by-side comparison of daily routes
- `plot_multi_day_gantt()` - Combined timeline across all days

### Interactive Maps (Folium)
Requires folium (install with `poetry install --with geo`):

**Features:**
- Clickable markers with detailed information
- Color-coded routes (single-day: gradient, multi-day: per-day colors)
- Popup windows showing arrival/departure times
- Numbered waypoints for route order
- Built on OpenStreetMap tiles
- Zoom and pan functionality
- Export as standalone HTML files

**Usage in notebook:**
```python
# Single day
viz.plot_interactive_map(solution, save=True)

# Multi-day
viz.plot_multi_day_interactive_map(multi_solution, save=True)
```

## Documentation

- **GETTING_STARTED.md** - Detailed setup guide
- **DATA_FORMAT_QUICK_REF.md** - Data structure reference
- **PROJECT_STATUS.md** - Current implementation status
- **CHANGELOG.md** - Version history
- **docs/** - Additional documentation

## Testing

```bash
# Run tests
pytest tests/

# Run specific test
python test_aco_debug.py
```

## Contributing

See project documentation for coding standards and contribution guidelines.

## License

Academic project for TU Wien - Self-Organizing Systems course.
