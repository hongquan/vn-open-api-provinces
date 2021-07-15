from pathlib import Path

from single_version import get_version


__version__ = get_version('vn-open-api-provinces', Path(__file__).parent.parent)
