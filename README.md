# WGUPS Routing — C950 DSA II

Lightweight WGUPS routing simulator used for WGU C950. Simulates three trucks delivering 40 packages using CSV inputs and a nearest-neighbor heuristic approach.

![Image](images/image.png)

## Contents
- Input Files:
  - `./Input Files/WGUPS Package File.csv`
  - `./Input Files/WGUPS Distance File.csv`
- Key code:
  - `main.py` — simulation entrypoint and routing logic
  - `truck.py`, `package.py`, `address.py`, `hashmap.py` — domain models & helpers

## Requirements
- Python 3.8+
- Recommended (Windows):
  - python -m venv venv
  - .\venv\Scripts\activate
  - pip install -r requirements.txt (if you add one)

## Run
- From project root:
  - python main.py

## How it works (brief)
1. Parse packages and distances into an address index and symmetric distance matrix.
2. Apply special rules:
   - Mark delayed packages (IDs 6, 25, 28, 32).
   - If the simulation snapshot time is after 10:20, update package 9's address.
3. Assign package lists to the three trucks (lists in `simulate_truck_deliveries`).
4. For truck 1 and 2 (then truck 3 after conditions), repeatedly:
   - Use `_find_nearest_delivery` (nearest neighbor) to select next stop.
   - Compute travel time using TRUCK_SPEED (18 mph).
   - Update package status, truck mileage, and times. Support partial-leg snapshots.
5. When a truck finishes, return it to HUB and add return miles.

## Notes
- Nearest-neighbor is a heuristic: results depend strongly on initial package distribution among trucks.
- This project is intentionally simple for the assignment; more advanced routing (2-opt, simulated annealing, or full TSP solvers) will reduce miles further.

## Contact / Next steps
- To get mileage under the target, try:
  - Re-balance package lists across trucks to cluster addresses.
  - Enhance `_find_nearest_delivery` to prefer deadline packages and small lookahead clustering.
  - Add per-leg debug output to trace mileage.