from dataclasses import asdict
from itertools import groupby
from operator import attrgetter
from collections import deque
from typing import List, FrozenSet, Dict, Any

from logbook import Logger
from fastapi import FastAPI, APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseSettings
from fastapi_rfc7807 import middleware

from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum

from .schema import ProvinceResponse, District as DistrictResponse, Ward as WardResponse


class Settings(BaseSettings):
    tracking: bool = False


logger = Logger(__name__)
app = FastAPI(title='Vietnam Provinces online API')
api = APIRouter()
settings = Settings()
middleware.register(app)


@api.get('/', response_model=List[ProvinceResponse])
async def show_all_divisions(depth: int = Query(1, ge=1, le=3,
                                                title='Show down to subdivisions',
                                                description='2: show districts; 3: show wards')):
    if depth >= 3:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    if depth == 2:
        provinces = deque()
        for k, group in groupby(DistrictEnum, key=attrgetter('value.province_code')):
            p = asdict(ProvinceEnum[f'P_{k}'].value)
            p['districts'] = tuple(asdict(d.value) for d in group)
            provinces.append(p)
        return provinces
    return tuple(asdict(p.value) for p in ProvinceEnum)


@api.get('/p/', response_model=List[ProvinceResponse])
async def list_provinces():
    return tuple(asdict(p.value) for p in ProvinceEnum)


@api.get('/p/{code}', response_model=ProvinceResponse)
async def get_province(code: int,
                       depth: int = Query(1, ge=1, le=3, title='Show down to subdivisions',
                                          description='2: show districts; 3: show wards')):
    try:
        province = ProvinceEnum[f'P_{code}'].value
    except KeyError:
        raise HTTPException(404, detail='invalid-province-code')
    response = asdict(province)
    districts = {}
    if depth >= 2:
        districts: Dict[int, Dict[str, Any]] = {d.value.code: asdict(d.value)
                                                for d in DistrictEnum if d.value.province_code == code}
    if depth == 3:
        district_codes: FrozenSet[int] = frozenset(districts.keys())
        for k, group in groupby(WardEnum, key=attrgetter('value.district_code')):
            if k not in district_codes:
                continue
            districts[k]['wards'] = tuple(asdict(w.value) for w in group)
    response['districts'] = tuple(districts.values())
    return response


@api.get('/d/', response_model=List[DistrictResponse])
async def list_districts():
    return tuple(asdict(d.value) for d in DistrictEnum)


@api.get('/d/{code}', response_model=DistrictResponse)
async def get_district(code: int,
                       depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions',
                                          description='2: show wards')):
    try:
        district = DistrictEnum[f'D_{code}'].value
    except KeyError:
        raise HTTPException(404, detail='invalid-district-code')
    response = asdict(district)
    if depth == 2:
        response['wards'] = tuple(asdict(w.value) for w in WardEnum if w.value.district_code == code)
    return response


@api.get('/w/', response_model=List[WardResponse])
async def list_wards():
    return tuple(asdict(w.value) for w in WardEnum)


@api.get('/w/{code}', response_model=WardResponse)
async def get_ward(code: int):
    try:
        ward = WardEnum[f'W_{code}'].value
    except KeyError:
        raise HTTPException(404, detail='invalid-ward-code')
    return asdict(ward)


app.include_router(api, prefix='/api')
