from enum import Enum
from typing import List, Dict, Tuple

from pydantic import BaseModel, Field

from vietnam_provinces.base import VietNamDivisionType


# The code here looks like a duplicate of vietnam_provinces.base, but unfortunately, we cannot subclass from
# vietnam_provinces.base's dataclasses, because:
# - Ward is frozen (fastenum's restriction), it cannot be subclass
# - FastAPI haven't supported dataclasses


class DivisionLevel(str, Enum):
    P = 'province'
    D = 'district'
    W = 'ward'


_EXAMPLE_WARD = {
    'name': 'Phường Phúc Xá',
    'code': 1,
    'division_type': 'phường',
    'codename': 'phuong_phuc_xa',
    'district_code': 1
}


class Ward(BaseModel):
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    district_code: int

    class Config:
        schema_extra = {
            'example': _EXAMPLE_WARD
        }


_EXAMPLE_DISTRICT = {
    'name': 'Quận Ba Đình',
    'code': 1,
    'division_type': 'quận',
    'codename': 'quan_ba_dinh',
    'province_code': 1,
    'wards': [_EXAMPLE_WARD]
}


class District(BaseModel):
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    province_code: int
    wards: List[Ward] = Field(default=[])

    class Config:
        schema_extra = {
            'example': _EXAMPLE_DISTRICT
        }


_EXAMPLE_PROVINCE = {
    'name': 'Thành phố Hà Nội',
    'code': 1,
    'division_type': 'thành phố trung ương',
    'codename': 'thanh_pho_ha_noi',
    'phone_code': 24,
    'districts': [_EXAMPLE_DISTRICT]
}


class ProvinceResponse(BaseModel):
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    phone_code: int
    districts: List[District] = Field(default=[])

    class Config:
        schema_extra = {
            'example': _EXAMPLE_PROVINCE
        }


class VersionResponse(BaseModel):
    data_version: str


class SearchResult(BaseModel):
    name: str
    code: int
    matches: Dict[str, Tuple[int, int]] = Field({}, title='Matched words and their positions in name.',
                                                description='This info can help client side highlight '
                                                'the result in display.')

    class Config:
        schema_extra = {
            'example': {
                'name': 'Thị xã Phú Mỹ',
                'code': 754,
                'matches': {
                    'mỹ': [11, 13]
                },
            }
        }
