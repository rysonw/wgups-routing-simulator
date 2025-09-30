from enum import Enum

class PackageStatus(Enum):
    AT_HUB = 1
    LOADED_IN_TRUCK = 2
    EN_ROUTE = 3
    DELIVERED = 4