from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, JsonValue
from pydantic.dataclasses import dataclass
from vietnam_provinces import Province, Ward


_EXAMPLE_PROVINCE: dict[str, JsonValue] = {
    'name': 'Thành phố Hà Nội',
    'code': 1,
    'division_type': 'thành phố trung ương',
    'codename': 'ha_noi',
    'phone_code': 24,
}

_EXAMPLE_WARD: dict[str, JsonValue] = {
    'name': 'Phường Bà Rịa',
    'code': 26560,
    'division_type': 'phường',
    'codename': 'phuong_ba_ria',
    'province_code': 79,
}

_EXAMPLE_WARD_WITH_LEGACY: dict[str, JsonValue] = {
    'source_code': 22855,
    'ward': _EXAMPLE_WARD,
}

_EXAMPLE_LEGACY_WARD: dict[str, JsonValue] = {
    'name': 'Xã Tân Hải',
    'code': 22855,
    'division_type': 'xã',
    'codename': 'tan_hai',
    'district_code': 748,
    'province_code': 77,
}


@dataclass(frozen=True, config=ConfigDict(json_schema_extra={'examples': [_EXAMPLE_PROVINCE]}))
class ProvinceResponse(Province):
    wards: Annotated[tuple[Ward, ...], Field(default_factory=tuple)]


@dataclass(frozen=True, config=ConfigDict(json_schema_extra={'examples': [_EXAMPLE_WARD]}))
class WardResponse(Ward):
    pass


@dataclass(frozen=True, config=ConfigDict(json_schema_extra={'examples': [_EXAMPLE_WARD_WITH_LEGACY]}))
class WardWithLegacySource:
    """Ward response with legacy source code."""
    source_code: int
    ward: WardResponse


class LegacyWardResponse(BaseModel):
    """Response model for legacy ward information."""
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_LEGACY_WARD]})
    name: str
    code: int
    division_type: str
    codename: str
    district_code: int
    province_code: int
