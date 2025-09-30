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

def _print_package_info(package):
    address = f"{package.address.street}, {package.address.city} {package.address.zip_code}"
    dt = getattr(package, "delivery_time", None)
    # format delivery time as time only (HH:MM:SS); show None or string otherwise
    if hasattr(dt, "strftime"):
        delivery = dt.strftime("%H:%M:%S")
    else:
        delivery = str(dt)
    print(f"ID: {package.id} | Address: {address} | Deadline: {package.deadline} | Assigned Truck: Truck {package.assigned_truck_number} | Status: {package.get_status_str()} | Delivery Time: {delivery}" )


def main_menu():
    """Top-level interactive loop.

    Process: show the main menu and dispatch a small set of demo actions. The
    full simulation code is present but commented out for the current demo.
    Flow: the loop reads a menu option and prints the corresponding action
    placeholder.

    Complexity: menu loop is O(1) per interaction.
    """

    # Start input loop (simple CLI)
    while True:
        user_input = show_main_menu()

        if user_input == "1":
            time.sleep(1)
            print("\n[Viewing All Packages...]\n")

            target_time = input("Enter a military time in the format HH:mm (or 'EOD' for end-of-day):\n").strip()
            if target_time.upper() == "EOD":
                snapshot_dt = datetime(2020, 1, 1, 23, 55, 0)
            else:
                try:
                    hh, mm = map(int, target_time.split(":"))
                    snapshot_dt = datetime(2020, 1, 1, hh, mm, 0)
                except Exception:
                    print("Invalid time format. Use HH:MM (e.g. 09:05) or 'EOD'. Returning to menu.")
                    input("Press Enter to return to the main menu...")
                    continue

            # Run the simulation up to the requested snapshot and get updated master list
            master_package_list = simulate_truck_deliveries(snapshot_dt)

            for id, package in sorted(master_package_list.items(), key=lambda k: k[0]):
                _print_package_info(package)    
            print()
            input("Press Enter to return to the main menu...")    

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
                snapshot_dt = datetime(2020, 1, 1, 17, 0, 0)
            else:
                try:
                    hh, mm = map(int, target_time.split(":"))
                    snapshot_dt = datetime(2020, 1, 1, hh, mm, 0)
                except Exception:
                    print("Invalid time format. Use HH:MM (e.g. 09:05) or 'EOD'. Returning to menu.")
                    input("Press Enter to return to the main menu...")
                    continue

            # Run the simulation up to the requested snapshot and get updated master list
            master_package_list = simulate_truck_deliveries(snapshot_dt)

            # Validate input is a valid package number
            if 1 <= package_id <= 40:
                package = master_package_list.get(package_id)
                if package:
                    _print_package_info(package)
                else:
                    print(f"Package {package_id} not found.")
                input("\nPress Enter to return to the main menu...")

            print("Invalid package id entered, please enter a valid id (1-40).")

        elif user_input == "3":
            time.sleep(1)
            print("\nShutting down WGUPS Routing Console...\n")
            time.sleep(1)
            sys.exit()
        else:
            time.sleep(1)
            print("\nInvalid option. Please try again.\n")
            time.sleep(1)

def simulate_truck_deliveries(end_time):
    """
    Run the day simulation up to `end_time` (a datetime on the same day).
    - Loads truck1/truck2 at 08:00, loads truck3 at 09:05 (delayed).
    - Uses nearest-neighbor per truck to pick next stop.
    - Advances trucks in event order and updates package objects in-place:
        pkg.load_time, pkg.delivery_time, pkg.package_status (or via set_package_status())
    - Returns a dict of master packages keyed by id (updated package objects).
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

    # Update Package 9 to new address, truck will leave at 10:20 to accomadate
    altered_package = master_list_packages.get(9)
    altered_package.address.street = "410 S State St"

    truck_1 = Truck(datetime(2020, 1, 1, 8, 0, 0), "HUB")
    truck_2 = Truck(datetime(2020, 1, 1, 10, 20, 0), "HUB")
    truck_3 = Truck(None, "HUB")

    t1_ids = [1, 8, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 40]
    t2_ids = [2, 3, 4, 5, 7, 10, 11, 12, 17, 18, 21, 22, 33, 36, 37, 38]
    t3_ids = [6, 9, 23, 24, 25, 26, 27, 28, 32, 35, 39]

    # Load packages
    for id in t1_ids:
        package = master_list_packages.get(id)
        package.assigned_truck_number = 1
        truck_1.add_package(package)

    for id in t2_ids:
        package = master_list_packages.get(id)
        package.assigned_truck_number = 2
        truck_2.add_package(package)

    for id in t3_ids:
        package = master_list_packages.get(id)

        if id in (25, 26):
            package.address.street = "5383 S 900 East #104"

        package.assigned_truck_number = 3
        truck_3.add_package(package)

    truck_1.is_in_use = True
    truck_2.is_in_use = True

    # Emulate each truck seperately till end_time
    # Complete truck_1 Route and then return then save end_time, this is the start time of truck_3
    # Finish truck_3 route
    for curr_truck in (truck_1, truck_2):
        # start this truck's route time from its departure_time
        ROUTE_TIME = curr_truck.departure_time

        # continue picking nearest package until no packages left or we've reached snapshot
        while ROUTE_TIME < end_time and len(curr_truck.get_packages()) > 0:
            # distances from truck's current street
            curr_addr_idx = address_index[curr_truck.current_address]
            curr_street_distances = distances[curr_addr_idx]

            # choose nearest package (skip None and current location)
            currLowest = None
            currLowest_pkg = None
            currLowest_idx = None
            package_list = curr_truck.get_packages()
            for package in package_list:
                package_idx = address_index.get(package.address.street)
                if package_idx is None:
                    continue
                dist = curr_street_distances[package_idx]
                if dist is None or package_idx == curr_addr_idx:
                    continue
                if currLowest is None or dist < currLowest:
                    currLowest = dist
                    currLowest_pkg = package
                    currLowest_idx = package_idx

            # nothing deliverable
            if currLowest_pkg is None:
                break

            # compute travel time for the leg
            distance = currLowest  # in miles
            travel_minutes = (distance / TRUCK_SPEED) * 60.0
            leg_duration = timedelta(minutes=travel_minutes)
            arrival_time = ROUTE_TIME + leg_duration

            # If we can complete this delivery before or at snapshot -> deliver
            if arrival_time <= end_time:
                # advance clock, update miles, set delivered
                ROUTE_TIME = arrival_time
                curr_truck.miles_traveled_today += distance
                # update truck location (store index or street as your Truck expects)
                try:
                    # if Truck expects address object/string
                    curr_truck.address = Address(street=list(address_index.keys())[currLowest_idx],
                                                 city="", state="", zip_code="")
                except Exception:
                    # fallback: set index if your Truck stores index
                    curr_truck.current_address_index = currLowest_idx

                # set package metadata
                currLowest_pkg.package_status = PackageStatus.DELIVERED
                currLowest_pkg.delivery_time = ROUTE_TIME
                
                try:
                    curr_truck.remove_package(currLowest_pkg)
                except Exception:
                    try:
                        curr_truck.get_packages().remove(currLowest_pkg)
                    except Exception:
                        pass

                # set truck's departure_time for next leg
                curr_truck.departure_time = ROUTE_TIME
                # loop will select next nearest package
                continue

            # Partial leg: cannot finish before snapshot -> advance partially and mark en route
            available_seconds = (end_time - ROUTE_TIME).total_seconds()
            leg_seconds = leg_duration.total_seconds()
            if available_seconds <= 0:
                break
            fraction = min(1.0, available_seconds / leg_seconds)
            partial_miles = distance * fraction
            curr_truck.miles_traveled_today += partial_miles
            # advance truck clock to snapshot
            ROUTE_TIME = end_time
            # mark package as en route (still on truck)
            currLowest_pkg.package_status = PackageStatus.EN_ROUTE
            if not hasattr(currLowest_pkg, "load_time"):
                currLowest_pkg.load_time = curr_truck.departure_time
            # update truck departure_time to snapshot so subsequent logic sees correct time
            curr_truck.departure_time = ROUTE_TIME
            # stop processing this truck (snapshot reached)
            break

    # load-time rule: truck_3 is available after delayed arrival (9:05) and after truck_1 finishes
    delayed_arrival = datetime(2020, 1, 1, 9, 5, 0)
    # determine when truck_1 finished its route (use its departure_time after loop)
    truck1_finish_time = getattr(truck_1, "departure_time", None) or datetime(2020, 1, 1, 8, 0, 0)
    # set truck_3 departure if it wasn't set and snapshot allows
    if len(truck_3.get_packages()) > 0:
        planned_depart = max(delayed_arrival, truck1_finish_time)
        if planned_depart <= end_time:
            truck_3.departure_time = planned_depart
            ROUTE_TIME = truck_3.departure_time
            # simulate truck_3 same as above
            while ROUTE_TIME < end_time and len(truck_3.get_packages()) > 0:
                curr_addr_idx = address_index[truck_3.current_address]
                curr_street_distances = distances[curr_addr_idx]

                currLowest = None
                currLowest_pkg = None
                currLowest_idx = None
                for package in truck_3.get_packages():
                    package_idx = address_index.get(package.address.street)
                    if package_idx is None:
                        continue
                    dist = curr_street_distances[package_idx]
                    if dist is None or package_idx == curr_addr_idx:
                        continue
                    if currLowest is None or dist < currLowest:
                        currLowest = dist
                        currLowest_pkg = package
                        currLowest_idx = package_idx

                if currLowest_pkg is None:
                    break

                distance = currLowest
                travel_minutes = (distance / TRUCK_SPEED) * 60.0
                leg_duration = timedelta(minutes=travel_minutes)
                arrival_time = ROUTE_TIME + leg_duration

                if arrival_time <= end_time:
                    ROUTE_TIME = arrival_time
                    truck_3.miles_traveled_today += distance
                    try:
                        truck_3.address = Address(street=list(address_index.keys())[currLowest_idx],
                                                  city="", state="", zip_code="")
                    except Exception:
                        truck_3.current_address_index = currLowest_idx

                    currLowest_pkg.package_status = PackageStatus.DELIVERED
                    currLowest_pkg.delivery_time = ROUTE_TIME
                    try:
                        truck_3.remove_package(currLowest_pkg)
                    except Exception:
                        try:
                            truck_3.get_packages().remove(currLowest_pkg)
                        except Exception:
                            pass
                    truck_3.departure_time = ROUTE_TIME
                    continue

                # partial leg for truck_3
                available_seconds = (end_time - ROUTE_TIME).total_seconds()
                leg_seconds = leg_duration.total_seconds()
                if available_seconds <= 0:
                    break
                fraction = min(1.0, available_seconds / leg_seconds)
                partial_miles = distance * fraction
                truck_3.miles_traveled_today += partial_miles
                ROUTE_TIME = end_time
                currLowest_pkg.package_status = PackageStatus.EN_ROUTE
                if not hasattr(currLowest_pkg, "load_time"):
                    currLowest_pkg.load_time = truck_3.departure_time
                truck_3.departure_time = ROUTE_TIME
                break

    try:
        num = 1
        for truck in (truck_1, truck_2, truck_3):
            _print_truck_information(truck, num)
            num += 1

        print(f"Total Mileage: {truck_1.miles_traveled_today + truck_2.miles_traveled_today + truck_3.miles_traveled_today}")
        print()
        return {k: v for k, v in master_list_packages.items()}
    except Exception:
        out = {}
        for i in range(1, 41):
            try:
                out[i] = master_list_packages.get(i)
            except Exception:
                out[i] = None
        return out
    
def _print_truck_information(truck, truck_num):
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
    print("1. View All Packages at a Specific Time")
    print("2. View Package by ID at a Specific Time")
    print("3. Exit")
    print("=========================================")

    # Get user choice safely
    choice = input("Enter your choice (1-3): ").strip()
    return choice


main_menu()