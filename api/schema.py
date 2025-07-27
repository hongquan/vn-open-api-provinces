from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict, JsonValue

from vietnam_provinces.base import VietNamDivisionType


# The code here looks like a duplicate of vietnam_provinces.base, but unfortunately, we cannot subclass from
# vietnam_provinces.base's dataclasses, because:
# - Ward is frozen (fastenum's restriction), it cannot be subclass
# - FastAPI haven't supported dataclasses


class DivisionLevel(str, Enum):
    P = 'province'
    D = 'district'
    W = 'ward'


_EXAMPLE_WARD: dict[str, JsonValue] = {
    'name': 'Phường Phúc Xá',
    'code': 1,
    'division_type': 'phường',
    'codename': 'phuong_phuc_xa',
    'district_code': 1,
}


class Ward(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_WARD]})
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    district_code: int


_EXAMPLE_DISTRICT: dict[str, JsonValue] = {
    'name': 'Quận Ba Đình',
    'code': 1,
    'division_type': 'quận',
    'codename': 'quan_ba_dinh',
    'province_code': 1,
    'wards': [_EXAMPLE_WARD],
}


class District(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_DISTRICT]})
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    province_code: int
    wards: Annotated[list[Ward], Field(default_factory=list)]


_EXAMPLE_PROVINCE: dict[str, JsonValue] = {
    'name': 'Thành phố Hà Nội',
    'code': 1,
    'division_type': 'thành phố trung ương',
    'codename': 'thanh_pho_ha_noi',
    'phone_code': 24,
    'districts': [_EXAMPLE_DISTRICT],
}


class ProvinceResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_PROVINCE]})
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    phone_code: int
    districts: Annotated[list[District], Field(default_factory=list)]


class VersionResponse(BaseModel):
    data_version: str


_EXAMPLE_MATCH: dict[str, JsonValue] = {
    'name': 'Thị xã Phú Mỹ',
    'code': 754,
    'matches': {'mỹ': [11, 13]},
}


class SearchResult(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_MATCH]})
    name: str
    code: int
    matches: Annotated[
        dict[str, tuple[int, int]],
        Field(
            {},
            title='Matched words and their positions in name.',
            description='This info can help client side highlight the result in display.',
        ),
    ]
