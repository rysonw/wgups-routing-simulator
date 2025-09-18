from address import Address
from truck import Truck
from hashmap import CustomHashMap
from driver import Driver

# CONST VARS
TRUCK_SPEED = 18.0

def simulate_single_operation_day():
    
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

    

def parse_package_csv():
    return

def parse_distance_csv():
    return