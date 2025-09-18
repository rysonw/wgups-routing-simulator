from truck import Truck

class Driver:
    def __init__(self, name, truck=None):
        self.name = name
        self.truck = truck

    def set_truck(self, truck):
        self.truck = truck

    def leave_truck(self):
        if self.truck.current_address == "Western Governors University 4001 South 700 East, Salt Lake City, UT 84107":
            self.truck = None
        else:
            print("You need to be at WGUPS HQ to leave this truck")