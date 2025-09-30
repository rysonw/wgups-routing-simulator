"""Package Model for WGUPS Simulator

Process:
  - Represent a WGUPS package with id, address, deadline, weight and status.
  - Provide small helper methods to set status and convert value types for easier printing to console.

Flow:
  - CSV parsing creates a Package for each row and stores it in the project's
    map. 
  - Throughout simulation, package statuses are updated as well as assigned truck numbers when loaded onto a specfic truck

Complexity:
  - Attribute access and small helper functions are O(1).
"""
from Enums.package_status import PackageStatus
from datetime import datetime

class Package:
    """Container for package data and light helpers.

    Process: store package fields and expose simple behavior used by the
    simulator

    Flow:
      - Created in parse_package_csv()
    """
    def __init__(self, id, address, deadline, weight, truck_number=None):
        self.id = id
        self.deadline = deadline
        self.weight = weight
        self.address = address
        self.truck_number = truck_number
        self.package_status = PackageStatus.AT_HUB
        self.delivery_time = None
        self.assigned_truck_number = None

    def set_package_status(self, status):
        """Set the package status.

        Process: Calidate the provided enum and set it to the package.

        Complexity: O(1).
        """
        if type(status) != type(PackageStatus):
            print("Please provide proper PackageStatus enum object")
        else:
            self.package_status = status
        
    def get_status_str(self):
        """Return a stringified enum value for output.

        Process: Simple switch, match up current status enum and return string.

        Complexity: O(1).
        """
        if self.package_status == PackageStatus.AT_HUB:
            return "At Hub"
        if self.package_status == PackageStatus.LOADED_IN_TRUCK:
            return f"Loaded on Truck {self.truck_number}"
        if self.package_status == PackageStatus.EN_ROUTE:
            return "En Route"
        if self.package_status == PackageStatus.DELIVERED:
            return "Delivered"
        # Fallback: return enum name if present, otherwise string representation
        try:
            return self.package_status.name
        except Exception:
            return str(self.package_status)
    

