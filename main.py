from address import Address
from truck import Truck
from hashmap import CustomHashMap
from driver import Driver
from package import Package
import csv
import re

# CONST VARS
TRUCK_SPEED = 18.0
DEFAULT_PACKAGE_CSV_ADDRESS = "C:/Users/ryson/Desktop/Anything CS/WGU/C950 - DSA 2/C950---DSA-2/Input Files/WGUPS Package File.csv"
DEFAULT_DISTANCE_CSV_ADDRESS = "C:/Users/ryson/Desktop/Anything CS/WGU/C950 - DSA 2/C950---DSA-2/Input Files/WGUPS Distance File.csv"

def simulate_single_operation_day():
    package_csv_file_location = "" #input("Please enter full path to WGUPS package csv file (Leave blank for default file in package): ")
    distance_csv_file_location = "" #input("Please enter full path to WGUPS distance csv file (Leave blank for default file in package): ")
    
    if package_csv_file_location:
        parse_package_csv(package_csv_file_location)
    else:
        parse_package_csv(DEFAULT_PACKAGE_CSV_ADDRESS)
    
    if distance_csv_file_location:
        addresses, address_index, distances = parse_distance_csv(package_csv_file_location)
    else:
        addresses, address_index, distances = parse_distance_csv(DEFAULT_DISTANCE_CSV_ADDRESS)

    print(addresses)
    print(address_index)
    print(distances)

    # Init Variables
    driver_1 = Driver("Marcus")
    driver_2 = Driver("Raja")

    truck1 = Truck()
    truck2 = Truck()
    truck3 = Truck()

    # Assign Relationships
    truck1.assign_driver(driver_1)
    truck1.is_in_use = True

    truck2.assign_driver(driver_2)
    truck2.is_in_use = True

    # Load Trucks

    # time_spent = distance / (18 * 60)

def calculate_nearest_neighbor(truck, address_map):
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

def parse_package_csv(path):
    map = CustomHashMap()
    with open(path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            address = Address(
                street=row[1].strip(),
                city=row[2].strip(),
                state=row[3].strip(),
                zip_code=row[4].strip()
            )

            pkg = Package(
                id=int(row[0]),
                address=address,
                deadline=row[5].strip(),
                weight=int(row[6]),
            )
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

#parse_package_csv()

simulate_single_operation_day()