class Truck:
    def __init__(self, truck_number, driver=None):
        self.packages = []
        self.driver = None
        self.current_address = ""
        self.truck_number = truck_number
        self.miles_traveled_today = 0
        self.is_in_use = False

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

    def assign_driver(self, driver):
        if self.driver == None:
            self.driver = driver
        else:
            print("Unassign current driver, {self.driver.name}, before assigning new driver to this truck.")

    def unassign_driver(self):
        if self.driver:
            self.driver.leave_truck()
        self.driver = None