"""Address model

Process:
    - Provide a small, plain data holder for an address used by Package objects.
    - This module defines a single class, Address, with four attributes.

Flow:
    - The constructor stores the provided street/city/state/zip_code values on the
        instance so other modules (main, package, truck) can read them.

Complexity:
    - Construction is O(1).
"""

class Address:
        """Simple address container.

        Process: store address components as attributes for easy access.
        Flow: callers create Address(...) once per package when parsing CSV rows.
        """
        def __init__(self, street, city, state, zip_code):
                # store raw address fields on the object
                self.street = street
                self.city = city
                self.state = state
                self.zip_code = zip_code

        def print(self):
            return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

