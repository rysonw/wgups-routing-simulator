from address import Address
from Enums.package_status import PackageStatus

class Package:
    def __init__(self, id, address, deadline, weight, truck_number=None):
        self.id = id
        self.deadline = deadline
        self.weight = weight
        self.address = address
        self.truck_number = truck_number
        self.package_status = PackageStatus.AT_HUB

    def set_package_status(self, status):
        if type(status) != type(PackageStatus):
            print("Please provide proper PackageStatus enum object")
        else:
            self.package_status = status
