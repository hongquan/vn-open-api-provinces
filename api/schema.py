from enum import Enum
from typing import List, Dict, Tuple
from dataclasses import field as dcfield

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from vietnam_provinces.base import VietNamDivisionType, District as _District


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


class WardConfig:
    schema_extra = {
        'example': _EXAMPLE_WARD
    }


@dataclass(config=WardConfig)
class Ward:
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    district_code: int


_EXAMPLE_DISTRICT = {
    'name': 'Quận Ba Đình',
    'code': 1,
    'division_type': 'quận',
    'codename': 'quan_ba_dinh',
    'province_code': 1,
    'wards': [_EXAMPLE_WARD]
}


class DistrictConfig:
    schema_extra = {
        'example': _EXAMPLE_DISTRICT
    }


@dataclass(config=DistrictConfig)
class District(dataclass(_District)):
    wards: List[Ward] = dcfield(default_factory=list)


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


class SearchResult(BaseModel):
    name: str
    code: int
    matches: Dict[str, Tuple[int, int]]
    score: int

    class Config:
        schema_extra = {
            'example': {
                'name': 'Thị xã Phú Mỹ',
                'code': 754,
                'matches': {
                    'mỹ': [11, 13]
                },
                'score': 3
            }
        }
