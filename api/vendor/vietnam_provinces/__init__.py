import os

# Vendor copy of vietnam_provinces library version 0.6.0

__data_version__ = "0.6.0"

# Path to the nested divisions JSON file.
# It is assumed that the data file is stored in the "data" directory inside this package.
NESTED_DIVISIONS_JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "nested_divisions.json")
