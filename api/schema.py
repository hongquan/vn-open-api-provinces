from typing import List
from dataclasses import field as dcfield

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from vietnam_provinces.base import VietNamDivisionType, District as _District


_EXAMPLE_WARD = {
    'name': 'Phường Phúc Xá',
    'code': 1,
    'division_type': 'phường',
    'codename': 'phuong_phuc_xa',
    'district_code': 1
}


@dataclass
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


@dataclass
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
    districts: List[District] = Field(default=[], example=[_EXAMPLE_DISTRICT])

    class Config:
        schema_extra = {
            'example': _EXAMPLE_PROVINCE
        }
