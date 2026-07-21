# Heavy-Lift Multirotor UAV Design Project

This directory contains the design methodology, engineering calculations, simulation models, and report generation scripts for a Heavy-Lift Multirotor UAV.

## Design Specifications

*   **Payload Capacity:** 10 kg
*   **Operational Range:** 30 km (15 km radius or 30 km out-and-back)
*   **Endurance:** ~2 hours (120 minutes) at full payload
*   **Max Propeller Size:** 40 inches
*   **Configuration:** Coaxial X8 Octocopter
*   **Power Source:** 3.6 kW Gas-Electric Hybrid Generator (with gasoline fuel tank and small LiPo buffer battery)

## Directory Structure

*   `design_calculations/`: Core mathematical models for the UAV sizing and performance.
    *   `propulsion.py`: Motor, ESC, battery, and propeller performance matching using Blade Element Momentum (BEM) and manufacturer data curves.
    *   `mass_budget.py`: Weight estimation, balance, and center of gravity calculations.
    *   `power_endurance.py`: Power consumption in hover/cruise, fuel burn rate, and range modeling.
    *   `structural_analysis.py`: Carbon fiber arm bending stress and landing gear impact calculations.
*   `simulation/`: Simulation scripts.
    *   `rotor_bem.py`: Blade Element Momentum (BEM) model for custom propeller blade profiles.
    *   `frame_fea.py`: Finite Element Method (FEM) solver for stress/deflection analysis under load factors (up to 2.5G).
*   `reports/`: Generated charts, diagrams, and final PDF assignment report.

## Quick Start

### Installation

Ensure you have Python 3 installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### Running Calculations & Simulations

To run all calculations, generate the plots, and compile the final PDF report:
```bash
python generate_report.py
```
*(This script will orchestrate all modules to verify calculations and write a detailed, formatted PDF report)*
