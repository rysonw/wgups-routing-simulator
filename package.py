from address import Address

class Package:
    def __init__(self):
        self.id = None
        self.address = None
        self.truck_number = None

    def set_packages(self, packages):
        if len(packages) > 16:
            return
        self.packages = packages

    def get_packages(self):
        return self.packages
    
    def add_package(self, package):
        if len(self.packages) + 1 > 16:
            return
        self.packages.append(package)
