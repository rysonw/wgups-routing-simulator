class Truck:
    def __init__(self, truck_number):
        self.packages = []
        self.driver = ""
        self.current_address = ""
        self.truck_number = truck_number
        self.miles_traveled_today = 0

    def set_packages(self, packages):
        if len(packages) > 16:
            return
        self.packages = packages

    def get_packages(self):
        return self.packages
    
    def add_packages(self, packages):
        if len(packages) + len(self.packages) > 16:
            return
        self.packages.append(packages)
