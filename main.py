"""
WGUPS Routing Main Program - 010369357

Process:
  - Provide CSV parsing helpers, simple simulation control and CLI menu for a
    simplified WGUPS routing exercise.

Flow:
  - parse_package_csv() reads package rows and stores Package objects in the
    project's CustomHashMap keyed by package id.
  - parse_distance_csv() builds an address list, index map and symmetric
    distance matrix used by routing helpers.
  - simulate_truck_deliveries() is the interactive
    loop used to simulate truck delivery operation.
"""

from address import Address
from truck import Truck
from hashmap import CustomHashMap
from package import Package
from datetime import datetime, timedelta
from Enums.package_status import PackageStatus
import csv
import re
import sys
import time

# CONST VARS
TRUCK_SPEED = 18.0
DEFAULT_PACKAGE_CSV_ADDRESS = "./Input Files/WGUPS Package File.csv"
DEFAULT_DISTANCE_CSV_ADDRESS = "./Input Files/WGUPS Distance File.csv"

def _print_package_info(package):
    """
    Prints the package info, used in both singular and all pacakge options

    Process: Extract all key values from package object
    Build f-string to print key information for user

    Complexity: All operations are instant -> O(1)
    """
    # Build address string
    dt = getattr(package, "delivery_time", None)
    if hasattr(dt, "strftime"):
        delivery = dt.strftime("%H:%M:%S")
    else:
        delivery = "N/A"

    # Custom print formatting for a normalized output
    print(
        f"ID: {package.id:<2} "
        f"| Address: {package.address.street:<40} "
        f"| City: {package.address.city:<16} "
        f"| Zip Code: {package.address.zip_code:<2} "
        f"| Weight: {package.weight:<2} Kg "
        f"| Deadline: {package.deadline:<10} "
        f"| Truck: {package.assigned_truck_number:<2} "
        f"| Status: {package.get_status_str():<10} "
        f"| Delivery Time: {delivery}"
    )

def main_menu():
    """
    Top-level interactive loop.

    Process: Show the main menu.
    Flow: The loop reads a menu option and prints the corresponding action
    placeholder. Continued until exit option is selected

    Complexity: Every interaction is O(1).
    """

    # Start input loop
    while True:
        user_input = show_main_menu()

        # All packages option
        if user_input == "1":
            time.sleep(1)
            print("\n[Viewing All Packages...]\n")

            # Choose what time to simulate delivery process till
            target_time = input("Enter a military time in the format HH:mm (or 'EOD' for end-of-day):\n").strip()
            print()
            if target_time.upper() == "EOD":
                snapshot_dt = datetime(2020, 1, 1, 23, 59, 0)
            else:
                try:
                    hh, mm = map(int, target_time.split(":"))
                    snapshot_dt = datetime(2020, 1, 1, hh, mm, 0)
                except Exception:
                    print("Invalid time format. Use HH:MM (e.g. 09:05) or 'EOD'. Returning to menu.")
                    input("Press Enter to return to the main menu...")
                    continue

            # Run the simulation up to the requested end_time and get master list
            # The Master List is a logbook of the statues of all package information
            master_package_list = simulate_truck_deliveries(snapshot_dt)

            # Hashmap is currently unsorted so we sort by package id here
            for _, package in sorted(master_package_list.items(), key=lambda k: k[0]):
                _print_package_info(package)    
            print()
            input("Press Enter to return to the main menu...")    

        # Singular package option
        elif user_input == "2":
            time.sleep(1)
            print("\n[Lookup Package by ID...]\n")
            package_id_str = input("Input target package id (1-40): ").strip()

            try:
                package_id = int(package_id_str)
            except ValueError:
                print("Invalid input; please enter a number between 1 and 40 (or 'q' to return).")
                continue

            target_time = input("Enter a military time in the format HH:mm (or 'EOD' for end-of-day):\n").strip()
            if target_time.upper() == "EOD":
                snapshot_dt = datetime(2020, 1, 1, 23, 59, 0)
            else:
                try:
                    hh, mm = map(int, target_time.split(":"))
                    snapshot_dt = datetime(2020, 1, 1, hh, mm, 0)
                except Exception:
                    print("Invalid time format. Use HH:MM (e.g. 09:05) or 'EOD'. Returning to menu.")
                    input("Press Enter to return to the main menu...")
                    continue

            # Run the simulation up to the requested snapshot and get master list
            # The Master List is a logbook of the statues of all package information
            master_package_list = simulate_truck_deliveries(snapshot_dt)

            # Validate input is a valid package number
            # Find specific package info and print to console
            if 1 <= package_id <= 40:
                package = master_package_list.get(package_id)
                if package:
                    _print_package_info(package)
                else:
                    print(f"Package {package_id} not found.")
                input("\nPress Enter to return to the main menu...")

            print("Invalid package id entered, please enter a valid id (1-40).")

        # Quit option
        elif user_input == "3":
            time.sleep(1)
            print("\nShutting down WGUPS Routing Console...\n")
            time.sleep(1)
            sys.exit()
        else:
            time.sleep(1)
            print("\nInvalid option. Please try again.\n")
            time.sleep(1)

def _calculate_return_to_hub(curr_truck, address_index, distances, ROUTE_TIME, TRUCK_SPEED):
    """
    Helper function to calculate distance when returning back
    to HUB after all packaes are delivered.

    Process: Calculate distance from current truck location to HUB, then add
    Flow: Get current address through truck attr. Find corresponding distance through address_index

    Complexity: O(1).
    """

    curr_addr_idx = address_index[curr_truck.current_address]
    hub_idx = address_index["HUB"]
    return_dist = distances[curr_addr_idx][hub_idx]
    return_minutes = (return_dist / TRUCK_SPEED) * 60.0
    curr_truck.miles_traveled_today += return_dist
    curr_truck.current_address = "HUB"
    return ROUTE_TIME + timedelta(minutes=return_minutes)

def _find_nearest_delivery(curr_location, packages, address_index, distances):
    """
    Find the next closest package destination from the current location.

    Process:
      - Look up the current address index.
      - Iterate through all undelivered packages, checking their address index.
      - Compute the distance from the current location to each package’s address.
      - Track the package with the smallest distance.

    Flow:
      - Returns a tuple (nearest_pkg, nearest_idx, nearest_dist).
      - If no valid package is found, returns (None, None, inf).

    Complexity: O(n), where n = number of packages on the truck.
    """

    # Initialize variables to return
    curr_idx = address_index[curr_location]
    nearest_dist = float('inf')
    nearest_pkg = None
    nearest_idx = None
    
    # Iterate through package list
    for package in packages:
        pkg_idx = address_index.get(package.address.street)
        if pkg_idx is None:
            continue
            
        dist = distances[curr_idx][pkg_idx]
        # Only update nearest pkg if the distance is the lower then what we have now
        if dist is not None and dist < nearest_dist:
            nearest_dist = dist
            nearest_pkg = package
            nearest_idx = pkg_idx
            
    return nearest_pkg, nearest_idx, nearest_dist

def simulate_truck_deliveries(end_time):
    """
    Simulates the delivery process for all WGUPS trucks up to a given time. Used for both "all
    package" and "siongualr package" menu options

    Process:
      - Load package and distance data from given CSV Files.
      - Apply special rules (delayed packages, corrected addresses).
      - Initialize three trucks with specific departure times:
          * Truck 1: 8:00 AM (time-sensitive packages).
          * Truck 2: 9:05 AM (waits for delayed packages).
          * Truck 3: 10:20 AM at the earliest, or once Truck 1 returns to hub.
      - Assign packages to trucks
      - For each truck, repeatedly select the nearest package destination using
        `_find_nearest_delivery` and simulate travel/delivery until:
          * All packages on the truck are delivered, or
          * The simulation snapshot time (`end_time`) is reached.
      - If a truck finishes all deliveries, calculate its return trip to the hub.
      - Update each package’s status (`DELAYED`, `EN_ROUTE`, `DELIVERED`) and record
        delivery times as appropriate.

    Flow:
      - Trucks are processed in sequence: Truck 1 → Truck 2 → Truck 3.
      - Each delivery leg updates mileage, current address, and package metadata.
      - Partial legs are supported if `end_time` occurs mid-delivery.
      - Returns a dictionary of all packages (id → Package object) with updated state.
      - Also prints per-truck statistics and total mileage traveled.

    Complexity:
      - Package lookups in the hash map: O(1) average.
      - Route simulation per truck: O(n²) worst case (nearest-neighbor heuristic across n packages).
      - Overall: O(n²), where n = number of packages.
    """
    # Load CSV Data
    master_list_packages = parse_package_csv(DEFAULT_PACKAGE_CSV_ADDRESS)
    _, address_index, distances = parse_distance_csv(DEFAULT_DISTANCE_CSV_ADDRESS)

    # Update values for special cases
    # Delayed Packages, updating statuses
    for pid in (6, 25, 28, 32):
        curr_package = master_list_packages.get(pid)
        curr_package.package_status = PackageStatus.DELAYED
        master_list_packages.add(pid, curr_package)

    # If given end time is past 10:20, update package 9 address
    if end_time >= datetime(2020, 1, 1, 10, 20, 0):
        curr_package = master_list_packages.get(9)
        curr_package.address.street = "410 S State St"
        curr_package.address.city = "Salt Lake City" 
        curr_package.address.zip_code = "84111"
        master_list_packages.add(9, curr_package)

    # Truck start times
    truck_1 = Truck(datetime(2020, 1, 1, 8, 0, 0), "HUB")
    truck_2 = Truck(datetime(2020, 1, 1, 9, 5, 0), "HUB")
    truck_3 = Truck(datetime(2020, 1, 1, 10, 20, 0), "HUB")

    # Package Id list
    t1_ids = [1, 13, 14, 15, 16, 20, 29, 30, 31, 34, 37, 40, 27, 33, 19]
    # Truck 2: packages that must be on Truck 2 AND delayed-on-flight packages (arrive ~9:05)
    t2_ids = [3, 18, 36, 38, 6, 25, 28, 32, 35, 39]
    t3_ids = [2, 4, 5, 7, 8, 9, 10, 11, 12, 17, 21, 22, 23, 24, 26]

    # Load packages
    for id in t1_ids:
        package = master_list_packages.get(id)
        package.assigned_truck_number = 1
        truck_1.add_package(package)

    for id in t2_ids:
        package = master_list_packages.get(id)

        # Reformat address here so it matches address in address_index
        if id in (25, 26):
            package.address.street = "5383 S 900 East #104"

        package.assigned_truck_number = 2
        truck_2.add_package(package)


    for id in t3_ids:
        package = master_list_packages.get(id)

        # Reformat address here so it matches address in address_index
        if id in (25, 26):
            package.address.street = "5383 S 900 East #104"

        package.assigned_truck_number = 3
        truck_3.add_package(package)

    # Start truck routing simulation
    for curr_truck in (truck_1, truck_2):
        ROUTE_TIME = curr_truck.departure_time

        # Continue picking nearest package until no packages left or we've reached end_time
        while ROUTE_TIME < end_time and len(curr_truck.get_packages()) > 0:
            # Find package with nearest address
            currLowest_pkg, _, currLowest = _find_nearest_delivery(
                curr_truck.current_address,
                curr_truck.get_packages(), 
                address_index,
                distances
            )

            # No packages
            if currLowest_pkg is None:
                break

            # Compute travel time for this leg
            distance = currLowest
            travel_minutes = (distance / TRUCK_SPEED) * 60.0
            leg_duration = timedelta(minutes=travel_minutes)
            arrival_time = ROUTE_TIME + leg_duration

            # If we can complete this delivery before or at snapshot -> deliver
            if arrival_time <= end_time:
                # Advance clock, Update miles, Set status to delivered
                ROUTE_TIME = arrival_time
                curr_truck.miles_traveled_today += distance
                curr_truck.current_address = currLowest_pkg.address.street

                # Set package metadata
                currLowest_pkg.package_status = PackageStatus.DELIVERED
                currLowest_pkg.delivery_time = ROUTE_TIME
                
                # Remove package from truck
                try:
                    curr_truck.remove_package(currLowest_pkg)
                except Exception:
                    try:
                        curr_truck.get_packages().remove(currLowest_pkg)
                    except Exception:
                        pass

                # Set truck's departure_time for next leg
                curr_truck.departure_time = ROUTE_TIME
                continue

            # Partial leg: cannot finish before end_time -> advance partially and mark en route
            available_seconds = (end_time - ROUTE_TIME).total_seconds()
            leg_seconds = leg_duration.total_seconds()
            if available_seconds <= 0:
                break
            # Find fraction and multiply to distance
            fraction = min(1.0, available_seconds / leg_seconds)
            partial_miles = distance * fraction
            curr_truck.miles_traveled_today += partial_miles
            # Advance clock to end_time
            ROUTE_TIME = end_time
            # Change package status to en route
            currLowest_pkg.package_status = PackageStatus.EN_ROUTE
            if not hasattr(currLowest_pkg, "load_time"):
                currLowest_pkg.load_time = curr_truck.departure_time
            # Update truck departure_time to snapshot so subsequent logic sees correct time
            curr_truck.departure_time = ROUTE_TIME
            # Stop processing this truck (END TIME REACHED)
            break 

        # If truck is empty, calculate the distance from current address to hub and add mileage
        if len(curr_truck.get_packages()) == 0:
            ROUTE_TIME = _calculate_return_to_hub(curr_truck, address_index, distances, ROUTE_TIME, TRUCK_SPEED)
            curr_truck.departure_time = ROUTE_TIME
            curr_truck.current_address = "HUB"

    # Set truck_3 departure as 10:20, truck_1 will finish and return to HUB before this (~9:40 am)
    if len(truck_3.get_packages()) > 0:
        planned_depart = datetime(2020, 1, 1, 10, 20, 0)
        if planned_depart <= end_time:
            truck_3.departure_time = planned_depart
            ROUTE_TIME = truck_3.departure_time
            
            # Continue picking nearest package until no packages left or we've reached end_time
            while ROUTE_TIME < end_time and len(truck_3.get_packages()) > 0:
                # Find package with nearest address
                currLowest_pkg, _, currLowest = _find_nearest_delivery(
                    truck_3.current_address,
                    truck_3.get_packages(), 
                    address_index,
                    distances
                )

                # No packages
                if currLowest_pkg is None:
                    break

                # Compute travel time for this leg
                distance = currLowest
                travel_minutes = (distance / TRUCK_SPEED) * 60.0
                leg_duration = timedelta(minutes=travel_minutes)
                arrival_time = ROUTE_TIME + leg_duration

                # If we can complete this delivery before or at snapshot -> deliver
                if arrival_time <= end_time:
                    # Advance clock, Update miles, Set status to delivered
                    ROUTE_TIME = arrival_time
                    truck_3.miles_traveled_today += distance
                    truck_3.current_address = currLowest_pkg.address.street

                    # Set package metadata
                    currLowest_pkg.package_status = PackageStatus.DELIVERED
                    currLowest_pkg.delivery_time = ROUTE_TIME
                    
                    # Remove package from truck
                    try:
                        truck_3.remove_package(currLowest_pkg)
                    except Exception:
                        try:
                            truck_3.get_packages().remove(currLowest_pkg)
                        except Exception:
                            pass

                    # Set truck's departure_time for next leg
                    truck_3.departure_time = ROUTE_TIME
                    continue

                # Partial leg: cannot finish before end_time -> advance partially and mark en route
                available_seconds = (end_time - ROUTE_TIME).total_seconds()
                leg_seconds = leg_duration.total_seconds()
                if available_seconds <= 0:
                    break
                # Find fraction and multiply to distance
                fraction = min(1.0, available_seconds / leg_seconds)
                partial_miles = distance * fraction
                truck_3.miles_traveled_today += partial_miles
                # Advance clock to end_time
                ROUTE_TIME = end_time
                # Change package status to en route
                currLowest_pkg.package_status = PackageStatus.EN_ROUTE
                if not hasattr(currLowest_pkg, "load_time"):
                    currLowest_pkg.load_time = truck_3.departure_time
                # Update truck departure_time to snapshot so subsequent logic sees correct time
                truck_3.departure_time = ROUTE_TIME
                # Stop processing this truck (END TIME REACHED)
                break

            # If truck is empty, calculate the distance from current address to hub and add mileage
            if len(truck_3.get_packages()) == 0:
                ROUTE_TIME = _calculate_return_to_hub(truck_3, address_index, distances, ROUTE_TIME, TRUCK_SPEED)
                truck_3.departure_time = ROUTE_TIME 
                truck_3.current_address = "HUB"

    # Console Output - Trucks
    # Use num for truck number
    num = 1
    for truck in (truck_1, truck_2, truck_3):
        _print_truck_information(truck, num)
        num += 1

    print(f"Total Mileage: {truck_1.miles_traveled_today + truck_2.miles_traveled_today + truck_3.miles_traveled_today}")
    print()
    return {k: v for k, v in master_list_packages.items()}

def _print_truck_information(truck, truck_num):
    """
    Prints a singular truck's key info
    Runtime: O(1)
    """
    print(f"Truck {truck_num} | Current Location: {truck.current_address} | Mileage: {truck.miles_traveled_today} miles | Number of Packages Left: {len(truck.packages)}")    

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
            """
            Process:
              - Skip headers and empty rows.
              - Extract address from column 2 and clean formatting.
              - Parse distance values from the rest of the row.

            Flow:
              - If row is empty or a header, continue.
              - Strip extra quotes and remove embedded ZIP codes from address.
              - Convert numeric distance values to floats, leave missing cells as None.
              - Append cleaned address and row distances to their respective lists.

            Complexity: O(m), where m = number of rows in the distance CSV.
            """
            if not row or not row[0].strip() or "DISTANCE" in row[0]:
                continue

            raw = row[1].strip().replace('"', "")
            if not raw:
                continue
            clean = re.sub(r"\(\d{5}\)", "", raw).strip()
            addresses.append(clean)

            row_distances = []
            for cell in row[2:]:
                if not cell.strip():
                    row_distances.append(None)
                else:
                    row_distances.append(float(cell))
            distances.append(row_distances)

    """
    Process:
      - Build a dictionary that maps each address to its index in the list.
      - Fill in missing (None) entries in the distance matrix by mirroring
        the corresponding non-None value from the opposite cell.

    Flow:
      - Use enumerate() to assign each address an index.
      - Iterate over i, j pairs and fill symmetric distances where needed.

    Complexity: O(n²), where n = number of addresses.
    """
    address_index = {addr: i for i, addr in enumerate(addresses)}

    n = len(addresses)
    for i in range(n):
        for j in range(n):
            if i < len(distances) and j < len(distances[i]):
                if distances[i][j] is None and distances[j][i] is not None:
                    distances[i][j] = distances[j][i]

    return addresses, address_index, distances

def show_main_menu():
    """
    Process: Output text art and menu to console, grabs input
    """
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
    print("1. View All Packages at a Specific Time")
    print("2. View Package by ID at a Specific Time")
    print("3. Exit")
    print("=========================================")

    # Get user choice safely
    choice = input("Enter your choice (1-3): ").strip()
    return choice


def run():
    """Entry point wrapper for running the WGUPS routing program."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nShutting down WGUPS Routing Console (Ctrl+C detected)...\n")
        sys.exit(0)


if __name__ == "__main__":
    run()