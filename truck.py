"""Truck model

Process:
  - Represent a delivery truck with a list of packages, driver, current
    address, and mileage tracking.

Flow:
  - The simulator will create Truck instances, assign drivers, load
    packages, advance current_time during travel, and deliver packages.

Complexity:
  - Most operations are O(1). Package list operations depend on list size.
"""


class Truck:
    """Simple truck container used by the simulator.

    Fields:
      - packages: list of Package objects currently loaded
      - driver: Driver assigned to the truck, or None
      - current_address: string for the current address
      - miles_traveled_today: total miles tracked for the day
      - is_in_use: flag indicating whether truck is active
      - departure_time: scheduled departure time
    """
    def __init__(self, departure_time, driver=None):
        # packages stored in a Python list; capacity limited to 16
        self.packages = []
        self.driver = None
        self.current_address = ""
        self.miles_traveled_today = 0
        self.is_in_use = False
        self.departure_time = departure_time

    def set_packages(self, packages):
        """Replace truck's package list if within capacity.

        Process: validate capacity then replace list reference (O(1)).
        """
        if len(packages) > 16:
            return
        self.packages = packages

    def get_packages(self):
        """Return current package list (O(1))."""
        return self.packages
    
    def add_packages(self, packages):
        """Append packages to the truck if capacity allows.

        Note: method expects `packages` to be a package or list element already
        prepared by parse/load logic. Guard against exceeding capacity.
        Complexity: O(1) for append, O(n) if list resizing occurs internally.
        """
        if len(packages) + len(self.packages) > 16:
            return
        self.packages.append(packages)

    def assign_driver(self, driver):
        """Assign a driver when none is currently assigned.

        Process: set driver reference, or print an informational message if a
        driver is already assigned.
        Complexity: O(1).
        """
        if self.driver == None:
            self.driver = driver
        else:
            print("Unassign current driver, {self.driver.name}, before assigning new driver to this truck.")

    def unassign_driver(self):
        """Unassign the driver and call their leave_truck hook.

        Flow: if driver exists, call Driver.leave_truck() which checks hub
        location before final unassignment.
        """
        if self.driver:
            self.driver.leave_truck()
        self.driver = None