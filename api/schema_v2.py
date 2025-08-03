from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue
from pydantic.dataclasses import dataclass
from vietnam_provinces import Province, Ward


_EXAMPLE_PROVINCE: dict[str, JsonValue] = {
    'name': 'Thành phố Hà Nội',
    'code': 1,
    'division_type': 'thành phố trung ương',
    'codename': 'thanh_pho_ha_noi',
    'phone_code': 24,
}


@dataclass(frozen=True, config=ConfigDict(json_schema_extra={'examples': [_EXAMPLE_PROVINCE]}))
class ProvinceResponse(Province):
    wards: Annotated[tuple[Ward, ...], Field(default_factory=list)]
