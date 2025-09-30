"""WGUPS routing program - main entrypoint and helpers.

Process:
  - Provide CSV parsing helpers, simple simulation control and CLI menu for a
    simplified WGUPS routing exercise.

Flow:
  - parse_package_csv() reads package rows and stores Package objects in the
    project's CustomHashMap keyed by package id.
  - parse_distance_csv() builds an address list, index map and symmetric
    distance matrix used by routing helpers.
  - simulate_single_operation_day() is the (currently simplified) interactive
    loop used to drive different views and simulations.
"""

from address import Address
from truck import Truck
from hashmap import CustomHashMap
from driver import Driver
from package import Package
from datetime import datetime, timedelta
from Enums.package_status import PackageStatus
import csv
import re
import sys
import time

# CONST VARS
TRUCK_SPEED = 18.0
DEFAULT_PACKAGE_CSV_ADDRESS = "C:/Users/ryson/Desktop/Anything CS/WGU/C950 - DSA 2/C950---DSA-2/Input Files/WGUPS Package File.csv"
DEFAULT_DISTANCE_CSV_ADDRESS = "C:/Users/ryson/Desktop/Anything CS/WGU/C950 - DSA 2/C950---DSA-2/Input Files/WGUPS Distance File.csv"


def simulate_single_operation_day():
    """Top-level interactive loop.

    Process: show the main menu and dispatch a small set of demo actions. The
    full simulation code is present but commented out for the current demo.
    Flow: the loop reads a menu option and prints the corresponding action
    placeholder.
    Complexity: menu loop is O(1) per interaction.
    """
    # package_csv_file_location = "" #input("Please enter full path to WGUPS package csv file (Leave blank for default file in package): ")
    # distance_csv_file_location = "" #input("Please enter full path to WGUPS distance csv file (Leave blank for default file in package): ")
    
    # if package_csv_file_location:
    #     undelivered_hub_packages = parse_package_csv(package_csv_file_location)
    # else:
    #     undelivered_hub_packages = parse_package_csv(DEFAULT_PACKAGE_CSV_ADDRESS)
    
    # if distance_csv_file_location:
    #     addresses, address_index, distances = parse_distance_csv(package_csv_file_location)
    # else:
    #     addresses, address_index, distances = parse_distance_csv(DEFAULT_DISTANCE_CSV_ADDRESS)

    # Start input loop (simple CLI)
    while True:
        user_input = show_main_menu()

        if user_input == "1":
            time.sleep(1)
            print("\n[Viewing All Packages...]\n")        
        elif user_input == "2":
            time.sleep(1)
            print("\n[Viewing Package by ID...]\n")                
        elif user_input == "3":
            time.sleep(1)
            print("\n[Viewing Truck Status...]\n")
        elif user_input == "4":
            time.sleep(1)
            print("\n[Simulating Deliveries...]\n")
        elif user_input == "5":
            time.sleep(1)
            print("\nShutting down WGUPS Routing Console...\n")
            time.sleep(1)
            sys.exit()
        else:
            time.sleep(1)
            print("\nInvalid option. Please try again.\n")
            time.sleep(1)

    # Simulate Deliveries
    # time_spent = distance / (TRUCK_SPEED * 60)


def load_packages(truck, package_list, hub_packages_map):
    """Load package objects onto a Truck from hub map.

    Process: iterate package IDs in package_list, mark each Package as
    LOADED_IN_TRUCK, append to truck, and remove from hub_packages_map.
    Complexity: O(k) where k is number of packages to load.
    """
    for p in package_list:
        p.set_package_status(PackageStatus.LOADED_IN_TRUCK)
        truck.add_packages(hub_packages_map.get(p))
        hub_packages_map.delete(p)


def calculate_nearest_neighbor(truck, address_map):
    """Choose the nearest package in the truck based on address_map distances.

    Process: look up the numeric address index for the truck's current
    address, then iterate truck.packages to find the package whose address
    yields the smallest distance from the current location.
    Complexity: O(m) where m is number of packages currently on the truck.
    """
    # Use current address to find which sub-array to reference 
    current_address = truck.current_address 
    current_package_list = truck.packages

    current_address_row = address_map[current_address]
    current_nearest_package = current_package_list[0]
    for package in current_package_list:
        # Iterate through all packages in the truck and find the one with the closest address
        distance_from_current_location = address_map[current_address_row][package.address.street]
        if distance_from_current_location < address_map[current_address_row][current_nearest_package.address.street]:
            current_nearest_package = package

    return current_nearest_package


def travel_and_deliver_next_package(truck, next_address, address_map, distances):
    """Advance the truck to next_address, update times and miles and return distance/minutes.

    Process: compute indices for from/to, pull precomputed distance from the
    distances matrix, compute minutes based on TRUCK_SPEED, and update the
    truck's current_time, miles_traveled, and current_address.
    Complexity: O(1).
    """
    from_index = address_map[truck.current_address]
    to_index = address_map[next_address]

    distance = distances[from_index][to_index]
    minutes = (distance / TRUCK_SPEED) * 60
    truck.current_time += timedelta(minutes=minutes)
    truck.miles_traveled += distance
    truck.current_address = to_index
    return distance, minutes


def parse_package_csv(path):
    """
    Loads WGUPS package data:
      - Extracts second column for addresses and rest of columns
      - Stores information in CustomHashMap using Package ID as the key
    Returns: CustomHashMap of packages keyed by id
    """
    # Create the map that will store package id -> Package object
    map = CustomHashMap()
    with open(path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            # Build Address object from CSV columns
            address = Address(
                street=row[1].strip(),
                city=row[2].strip(),
                state=row[3].strip(),
                zip_code=row[4].strip()
            )

            # Build Package object from CSV columns
            pkg = Package(
                id=int(row[0]),
                address=address,
                deadline=row[5].strip(),
                weight=int(row[6]),
            )
            # Insert into the map keyed by package id
            map.add(pkg.id, pkg)
    file.close()
    # Note: map.items() returns bucket-ordered items; sort for human-friendly output
    print(sorted(map.items(), key=lambda kv: kv[0]))
    return map


def parse_distance_csv(path):
    """
    Loads WGUPS distance table:
      - Extracts street addresses from column 2 (no ZIP codes).
      - Builds address_index for quick lookup.
      - Builds full distance matrix with mirrored values.
    Returns: (addresses, address_index, distances)
    """
    addresses = []
    address_index = {}
    distances = []

    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            # skip empty rows and headers
            if not row or not row[0].strip() or "DISTANCE" in row[0]:
                continue

            # --- Step 1: clean address from column 2 ---
            raw = row[1].strip().replace('"', "")
            if not raw:
                continue
            clean = re.sub(r"\(\d{5}\)", "", raw).strip()
            addresses.append(clean)

            # --- Step 2: distances for this row (starting at col 2 onward) ---
            row_distances = []
            for cell in row[2:]:
                if not cell.strip():
                    row_distances.append(None)
                else:
                    row_distances.append(float(cell))
            distances.append(row_distances)

    # --- Step 3: build index map ---
    address_index = {addr: i for i, addr in enumerate(addresses)}

    # --- Step 4: fill mirrored values ---
    n = len(addresses)
    for i in range(n):
        for j in range(n):
            if i < len(distances) and j < len(distances[i]):
                if distances[i][j] is None and distances[j][i] is not None:
                    distances[i][j] = distances[j][i]

    return addresses, address_index, distances


def is_on_time(package):
    # Return True if package.delivery_time is on or before package.deadline
    return package.delivery_time.time() <= package.deadline


def travel_time(distance):
    hours = distance / 18.0
    return timedelta(hours=hours)


def deliver_package(truck, package, distance):
    # advance time by travel duration
    travel = travel_time(distance)
    truck.current_time += travel

    # mark package delivered
    package.delivery_time = truck.current_time
    package.status = "Delivered"

    # track miles
    truck.miles_driven += distance


def show_main_menu():
    banner = r"""
__        ______ _   _ ____  ____    ____            _                    
\ \      / / ___| | | |  _ \/ ___|  |  _ \ __ _  ___| | ____ _  __ _  ___ 
 \ \ /\ / / |  _| | | | |_) \___ \  | |_) / _` |/ __| |/ / _` |/ _` |/ _ \
  \ V  V /| |_| | |_| |  __/ ___) | |  __/ (_| | (__|   < (_| | (_| |  __/
   \_/\_/  \____|\___/|_|   |____/  |_|   \__,_|\___|_|\_\__,_|\__, |\___|
 ____             _   _                ____                    |___/      
|  _ \ ___  _   _| |_(_)_ __   __ _   / ___|___  _ __  ___  ___ | | ___   
| |_) / _ \| | | | __| | '_ \ / _` | | |   / _ \| '_ \/ __|/ _ \| |/ _ \  
|  _ < (_) | |_| | |_| | | | | (_| | | |__| (_) | | | \__ \ (_) | |  __/  
|_| \_\___/ \__,_|\__|_|_| |_|\__, |  \____\___/|_| |_|___/\___/|_|\___|  
                              |___/                                       
    """
    print(banner)
    print("=========================================")
    print("        WGUPS Routing Program Menu       ")
    print("=========================================")
    print("1. View All Packages")
    print("2. View Package by ID")
    print("3. View Truck Status")
    print("4. Simulate Deliveries")
    print("5. Exit")
    print("=========================================")

    # Get user choice safely
    choice = input("Enter your choice (1-5): ").strip()
    return choice


simulate_single_operation_day()