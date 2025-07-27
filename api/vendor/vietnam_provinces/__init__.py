from pathlib import Path

from .base import VietNamDivisionType, Province, District, Ward


__version__ = '0.6.0'
# Data retrieval date, in UTC
__data_version__ = '2025-01-04'
NESTED_DIVISIONS_JSON_PATH = Path(__file__).parent / 'data' / 'nested-divisions.json'
FLAT_DIVISIONS_JSON_PATH = Path(__file__).parent / 'data' / 'flat-divisions.json'
