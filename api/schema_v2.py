from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, JsonValue
from vietnam_provinces import VietNamDivisionType, Ward


_EXAMPLE_PROVINCE: dict[str, JsonValue] = {
    'name': 'Thành phố Hà Nội',
    'code': 1,
    'division_type': 'thành phố trung ương',
    'codename': 'thanh_pho_ha_noi',
    'phone_code': 24,
}


class ProvinceResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={'examples': [_EXAMPLE_PROVINCE]})
    name: str
    code: int
    division_type: VietNamDivisionType
    codename: str
    phone_code: int
    wards: Annotated[list[Ward], Field(default_factory=list)]
