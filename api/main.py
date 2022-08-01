import os
from dataclasses import asdict
from itertools import groupby
from operator import attrgetter
from collections import deque
from typing import List, FrozenSet, Dict, Any, Optional

from logbook import Logger
from logbook.more import ColorizedStderrHandler
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseSettings
from fastapi_rfc7807 import middleware
from lunr.exceptions import QueryParseError

from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum
from vietnam_provinces.enums.wards import WardEnum

from . import __version__
from .schema import ProvinceResponse, District as DistrictResponse, Ward as WardResponse, SearchResult
from .search import Searcher


class Settings(BaseSettings):
    tracking: bool = False
    cdn_cache_interval: int = 30


logger = Logger(__name__)
app = FastAPI(title='Vietnam Provinces online API', version=__version__)
api = APIRouter()
settings = Settings()
middleware.register(app)
repo = Searcher()
ColorizedStderrHandler().push_application()


SearchResults = List[SearchResult]
SearchQuery = Query(..., title='Query string for search', example='Hiền Hòa',
                    description='Follow [lunr](https://lunr.readthedocs.io/en/latest/usage.html#using-query-strings)'
                    ' syntax.')


@api.get('/', response_model=List[ProvinceResponse])
async def show_all_divisions(request: Request,
                             depth: int = Query(1, ge=1, le=3,
                                                title='Show down to subdivisions',
                                                description='2: show districts; 3: show wards')):
    client_ip = request.client.host
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = (s.strip() for s in env_value.split(','))
        if client_ip in blacklist:
            logger.info('{} is blacklisted.', client_ip)
            raise HTTPException(429)
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


@api.get('/p/search/', response_model=SearchResults)
async def search_provinces(q: str = SearchQuery):
    try:
        res = repo.search_province(q)
        return res
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api.get('/p/{code}', response_model=ProvinceResponse)
async def get_province(code: int,
                       depth: int = Query(1, ge=1, le=3, title='Show down to subdivisions',
                                          description='2: show districts; 3: show wards')):
    try:
        province = ProvinceEnum[f'P_{code}'].value
    except (KeyError, AttributeError):
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


@api.get('/d/search/', response_model=SearchResults)
async def search_districts(q: str = SearchQuery,
                           p: Optional[int] = Query(None, title='Province code to filter')):
    try:
        return repo.search_district(q, p)
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api.get('/d/{code}', response_model=DistrictResponse)
async def get_district(code: int,
                       depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions',
                                          description='2: show wards')):
    try:
        district = DistrictEnum[f'D_{code}'].value
    except (KeyError, AttributeError):
        raise HTTPException(404, detail='invalid-district-code')
    response = asdict(district)
    if depth == 2:
        response['wards'] = tuple(asdict(w.value) for w in WardEnum if w.value.district_code == code)
    return response


@api.get('/w/', response_model=List[WardResponse])
async def list_wards():
    return tuple(asdict(w.value) for w in WardEnum)


@api.get('/w/search/', response_model=SearchResults)
async def search_wards(q: str = SearchQuery,
                       d: Optional[int] = Query(None, title='District code to filter'),
                       p: Optional[int] = Query(None, title='Province code to filter, ignored if district is given')):
    try:
        return repo.search_ward(q, d, p)
    except QueryParseError:
        raise HTTPException(status_code=422, detail='unrecognized-search-query')


@api.get('/w/{code}', response_model=WardResponse)
async def get_ward(code: int):
    try:
        ward = WardEnum[f'W_{code}'].value
    except (KeyError, AttributeError):
        raise HTTPException(404, detail='invalid-ward-code')
    return asdict(ward)


@api.get('/_client_ip')
async def get_client_ip(request: Request):
    return request.client.host


app.include_router(api, prefix='/api')


@app.middleware('http')
async def guide_cdn_cache(request: Request, call_next):
    response = await call_next(request)
    # Ref: https://vercel.com/docs/edge-network/headers#cache-control-header
    response.headers['Cache-Control'] = f's-maxage={settings.cdn_cache_interval}, stale-while-revalidate'
    return response


# Vercel ASGI server doesn't support "startup" event, so we have to run this code in global
logger.debug('To build search index')
repo.build_index()
logger.debug('Ready to search')
