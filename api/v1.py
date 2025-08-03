import os
from collections import deque
from dataclasses import asdict
from itertools import groupby
from operator import attrgetter
from typing import Any, Deque, FrozenSet

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from lunr.exceptions import QueryParseError

from .schema_v1 import District as DistrictResponse
from .schema_v1 import ProvinceResponse, SearchResult, VersionResponse
from .schema_v1 import Ward as WardResponse
from .search import repo
from .vendor.vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, __data_version__
from .vendor.vietnam_provinces.enums.districts import DistrictEnum, ProvinceEnum
from .vendor.vietnam_provinces.enums.wards import WardEnum


api_v1 = APIRouter()

SearchResults = list[SearchResult]
SearchQuery = Query(
    ...,
    title='Query string for search',
    example='Hiền Hòa',
    description='Follow [lunr](https://lunr.readthedocs.io/en/latest/usage.html#using-query-strings) syntax.',
)


@api_v1.get('/', response_model=list[ProvinceResponse])
async def show_all_divisions(
    request: Request,
    depth: int = Query(
        1, ge=1, le=3, title='Show down to subdivisions', description='2: show districts; 3: show wards'
    ),
):
    client_ip = request.client.host if request.client else None
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = filter(None, (s.strip() for s in env_value.split(',')))
        if not client_ip or client_ip in blacklist:
            raise HTTPException(429)
    if depth >= 3:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    if depth == 2:
        provinces: Deque[dict[str, Any]] = deque()
        for k, group in groupby(DistrictEnum, key=attrgetter('value.province_code')):
            p = asdict(ProvinceEnum[f'P_{k}'].value)
            p['districts'] = tuple(asdict(d.value) for d in group)
            provinces.append(p)
        return provinces
    return tuple(asdict(p.value) for p in ProvinceEnum)


@api_v1.get('/p/', response_model=list[ProvinceResponse])
async def list_provinces():
    return tuple(asdict(p.value) for p in ProvinceEnum)


@api_v1.get('/p/search/', response_model=SearchResults)
async def search_provinces(q: str = SearchQuery):
    try:
        res = repo.search_province(q)
        return res
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api_v1.get('/p/{code}', response_model=ProvinceResponse)
async def get_province(
    code: int,
    depth: int = Query(
        1, ge=1, le=3, title='Show down to subdivisions', description='2: show districts; 3: show wards'
    ),
):
    try:
        province = ProvinceEnum[f'P_{code}'].value
    except (KeyError, AttributeError):
        raise HTTPException(404, detail='invalid-province-code')
    response = asdict(province)
    districts: dict[int, dict[str, Any]] = {}
    if depth >= 2:
        districts = {d.value.code: asdict(d.value) for d in DistrictEnum if d.value.province_code == code}
    if depth == 3:
        district_codes: FrozenSet[int] = frozenset(districts.keys())
        for k, group in groupby(WardEnum, key=attrgetter('value.district_code')):
            if k not in district_codes:
                continue
            districts[k]['wards'] = tuple(asdict(w.value) for w in group)
    response['districts'] = tuple(districts.values())
    return response


@api_v1.get('/d/', response_model=list[DistrictResponse])
async def list_districts():
    return tuple(asdict(d.value) for d in DistrictEnum)


@api_v1.get('/d/search/', response_model=SearchResults)
async def search_districts(q: str = SearchQuery, p: int | None = Query(None, title='Province code to filter')):
    try:
        return repo.search_district(q, p)
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api_v1.get('/d/{code}', response_model=DistrictResponse)
async def get_district(
    code: int, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions', description='2: show wards')
):
    try:
        district = DistrictEnum[f'D_{code}'].value
    except (KeyError, AttributeError):
        raise HTTPException(404, detail='invalid-district-code')
    response = asdict(district)
    if depth == 2:
        response['wards'] = tuple(asdict(w.value) for w in iter(WardEnum) if w.value.district_code == code)
    return response


@api_v1.get('/w/', response_model=list[WardResponse])
async def list_wards():
    return tuple(asdict(w.value) for w in WardEnum)


@api_v1.get('/w/search/', response_model=SearchResults)
async def search_wards(
    q: str = SearchQuery,
    d: int | None = Query(None, title='District code to filter'),
    p: int | None = Query(None, title='Province code to filter, ignored if district is given'),
):
    try:
        return repo.search_ward(q, d, p)
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api_v1.get('/w/{code}', response_model=WardResponse)
async def get_ward(code: int):
    try:
        ward = WardEnum[f'W_{code}'].value  # type: ignore[misc]
    except (KeyError, AttributeError):
        raise HTTPException(404, detail='invalid-ward-code')
    return asdict(ward)


@api_v1.get('/version', response_model=VersionResponse)
async def get_version():
    return VersionResponse(data_version=__data_version__)
