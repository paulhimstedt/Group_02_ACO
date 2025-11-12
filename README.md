# Vienna Christmas Market Route Optimizer

## Project Overview
This project solves the time-constrained Christmas market visiting problem using Ant Colony Optimization (ACO) and other heuristic approaches. The goal is to maximize the number of markets visited within opening hours constraints.

## Team Structure
- **Data Preparation & API Integration**: Teammate
- **Modeling & Optimization**: Current focus (this implementation)

## Problem Description
Given a set of Christmas markets in Vienna with:
- Different opening and closing times
- Travel times between markets (walking/public transport)
- Limited visiting time per day
- Required stay duration at each market

Find an optimal route that maximizes the number of markets visited.

## Repository Structure
```
.
├── data/                      # Data directory
│   ├── demo/                  # Demo data for development
│   └── real/                  # Real data (populated by teammate)
├── src/                       # Source code
│   ├── models/                # Optimization models (ACO, Greedy, etc.)
│   ├── utils/                 # Helper functions
│   └── visualization/         # Plotting and animation tools
├── config/                    # Configuration files
├── notebooks/                 # Jupyter notebooks for analysis
├── tests/                     # Unit tests
├── results/                   # Output results and figures
└── docs/                      # Documentation
```

## Key Features
- Configurable parameters (stay duration, number of days, etc.)
- Multiple optimization algorithms (ACO, Greedy, Genetic Algorithm)
- Comprehensive visualization (routes, statistics, animations)
- Multi-day planning support
- Demo data for testing

## Installation

### Using Poetry (Recommended)
```bash
# Install dependencies
poetry install

# Optional: Install geospatial extras for map visualization
poetry install --with geo

# Activate virtual environment
poetry shell
```

### Using pip (Alternative)
```bash
# Export dependencies from Poetry
poetry export -f requirements.txt --output requirements.txt

# Install with pip
pip install -r requirements.txt
```

## Quick Start

### With Poetry
```bash
poetry run optimize --config config/default.yaml
# or
poetry run python src/main.py --config config/default.yaml
```

### Without Poetry
```bash
python src/main.py --config config/default.yaml
```

## Configuration
See `config/default.yaml` for all configurable parameters including:
- Market stay duration
- Number of days
- Algorithm parameters
- Visualization options

## Documentation
Detailed documentation available in `docs/` directory.
