"""Driver model

Process:
  - Simple object representing a driver assigned to a truck.
  - Exposes methods to assign/unassign trucks and guard leaving logic.

Flow:
  - Created during simulation setup and assigned to Truck instances.
  - leave_truck() verifies the driver is at the hub before unassigning.

Complexity:
  - All methods are O(1).
"""

class Driver:
    """Represents a driver who may be assigned a truck.

    Process: hold a reference to the assigned truck and allow simple
    operations like set_truck and leave_truck.
    Flow: the simulator assigns drivers to trucks during setup and may call
    leave_truck when the driver should step away.
    """
    def __init__(self, name, truck=None):
        # store identifying name and optional Truck reference
        self.name = name
        self.truck = truck

    def set_truck(self, truck):
        """Assign a Truck instance to this driver (O(1))."""
        self.truck = truck

    def leave_truck(self):
        """Unassign the truck if the driver is at the WGUPS HQ address.

        Process: check the truck's current_address string for the hub address
        and only unassign when at the hub. This prevents leaving a truck at a
        delivery location.
        Complexity: O(1).
        """
        if self.truck.current_address == "Western Governors University 4001 South 700 East, Salt Lake City, UT 84107":
            self.truck = None
        else:
            print("You need to be at WGUPS HQ to leave this truck")