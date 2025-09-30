"""Truck Model for WGUPS Simulator

Process:
  - Represent a delivery truck with a list of packages, current
    address, and total mileage.

Flow:
  - The simulator will create Truck instances, load a list of static 
  packages, advance current_time during travel, and deliver packages.

Complexity:
  - Most operations are O(1). Package list operations depend on list size.
"""

class Truck:
    """Simple truck container used by the simulator.

    Fields:
      - packages: list of Package objects currently loaded
      - current_address: string for the current street address only
      - miles_traveled_today: total miles tracked for the day for this specific truck
      - is_in_use: flag indicating whether truck is active, 2 trucks active at the most
      - departure_time: scheduled departure time, timedate object
    """
    def __init__(self, departure_time, address):
        self.packages = []
        self.current_address = address
        self.miles_traveled_today = 0
        self.is_in_use = False
        self.departure_time = departure_time

    def get_packages(self):
        """Return current package list, Complexity: O(1)."""
        return self.packages
    
    def add_package(self, package):
        """
        Append a single package to the truck if capacity allows.
        Complexity: O(1) for append, O(n) if list resizing occurs internally.
        """
        if len(self.packages) + 1 > 16:
            return
        self.packages.append(package)