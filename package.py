"""Package model

Process:
  - Represent a WGUPS package with id, address, deadline, weight and status.
  - Provide small helper methods to set status and convert deadlines.

Flow:
  - CSV parsing creates a Package for each row and stores it in the project's
    map. Delivery simulation updates status and delivery_time on these objects.

Complexity:
  - Attribute access and small helper functions are O(1).
"""

from address import Address
from Enums.package_status import PackageStatus
from datetime import datetime


class Package:
    """Container for package data and light helpers.

    Process: store package fields and expose simple behavior used by the
    simulator (status updates, deadline parsing, on-time checks).

    Flow:
      - Created in parse_package_csv()
      - Status is updated by load_packages() and delivery functions
      - Delivery times are compared to the parsed deadline via is_on_time()
    """
    def __init__(self, id, address, deadline, weight, truck_number=None):
        # store fundamental package attributes
        self.id = id
        self.deadline = deadline
        self.weight = weight
        self.address = address
        self.truck_number = truck_number
        self.package_status = PackageStatus.AT_HUB

    def set_package_status(self, status):
        """Set the package status.

        Process: validate the provided enum and set the internal state.
        Flow: callers pass a PackageStatus; if invalid we print an error and do
        not change state.
        Complexity: O(1).
        """
        if type(status) != type(PackageStatus):
            print("Please provide proper PackageStatus enum object")
        else:
            self.package_status = status

    def get_deadline(self, deadline):
        """Parse a deadline string into a time object.

        Process: 'EOD' is treated as 5:00 PM, otherwise parse 'HH:MM AM/PM'.
        Flow: Used when comparing delivery times to required deadlines.
        Complexity: O(1) (constant-time parsing).
        """
        if deadline == "EOD":
            return datetime.strptime("05:00 PM", "%I:%M %p").time()
        else:
            return datetime.strptime(deadline, "%I:%M %p").time()

    def is_on_time(self, package_delivery_time, departure_time):
        """Return True if package was delivered on or before the deadline.

        Process: compare delivery timestamp + departure_time against the
        stored deadline. Note: the simulator is responsible for providing
        timestamps in compatible units.
        Complexity: O(1).
        """
        if package_delivery_time + departure_time <= self.deadline:
            return True
        else:
            return False
    

