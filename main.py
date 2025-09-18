from address import Address
from truck import Truck
from hashmap import CustomHashMap
from driver import Driver
from package import Package
import csv
from dataclasses import dataclass

# CONST VARS
TRUCK_SPEED = 18.0

def simulate_single_operation_day():
    package_csv_file_location = input("Please enter full path to WGUPS package csv file: ")
    distance_csv_file_location = input("Please enter full path to WGUPS distance csv file: ")
    
    parse_distance_csv(distance_csv_file_location)
    parse_package_csv(package_csv_file_location)

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

def calculate_nearest_neighbor(current_address):
    return

def parse_package_csv(path):
    map = {}
    with open(path, newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
            address = Address(
                address=row[1].strip(),
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
            map[pkg.id] = pkg
    file.close()
    return map

def parse_distance_csv(path):
    return

#simulate_single_operation_day()