class Package:
    def __init__(self):
        self.id = ""
        self.address = ""
        self.truck_number = None

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
