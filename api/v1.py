import os
from dataclasses import asdict
from operator import attrgetter

from fastapi import FastAPI, HTTPException, Query, Request
from logbook import Logger
from vietnam_provinces import __data_version__
from vietnam_provinces.legacy import District, DistrictCode, Province, ProvinceCode, Ward, WardCode

from . import __version__
from .schema_v1 import District as DistrictResponse
from .schema_v1 import ProvinceResponse, SearchResult, VersionResponse
from .schema_v1 import Ward as WardResponse


logger = Logger(__name__)

api_v1 = FastAPI(title='Vietnam Provinces online API', version=__version__)

SearchResults = list[SearchResult]
SearchQuery = Query(
    ...,
    title='Query string for search',
    examples=['Hiền Hòa'],
    description='Enter full or partial name. Example: "Hiền Hòa" or "hien hoa".',
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

    provinces = []
    for p in sorted(Province.iter_all(), key=attrgetter('code')):
        pd = asdict(p)
        if depth >= 2:
            districts = []
            for d in sorted(District.iter_by_province(p.code), key=attrgetter('code')):
                dd = asdict(d)
                if depth >= 3:
                    dd['wards'] = tuple(
                        asdict(w) for w in sorted(Ward.iter_by_district(d.code), key=attrgetter('code'))
                    )
                districts.append(dd)
            pd['districts'] = tuple(districts)
        else:
            pd['districts'] = ()
        provinces.append(pd)
    return provinces


@api_v1.get('/p/', response_model=list[ProvinceResponse])
async def list_provinces():
    return tuple(asdict(p) for p in sorted(Province.iter_all(), key=attrgetter('code')))


def _make_search_results(items) -> list[dict]:
    # Try to extract the enum value safely
    def _code_value(code):
        if hasattr(code, 'value'):
            return code.value
        return code

    return [{'name': i.name, 'code': _code_value(i.code)} for i in items]


@api_v1.get('/p/search/', response_model=SearchResults)
async def search_provinces(q: str = SearchQuery):
    items = Province.search(q)
    return _make_search_results(items)


@api_v1.get('/p/{code}', response_model=ProvinceResponse)
async def get_province(
    code: int,
    depth: int = Query(
        1, ge=1, le=3, title='Show down to subdivisions', description='2: show districts; 3: show wards'
    ),
):
    try:
        pcode = ProvinceCode(code)
    except ValueError:
        raise HTTPException(404, detail='invalid-province-code')
    try:
        province = Province.from_code(pcode)
    except (KeyError, ValueError, IndexError):
        raise HTTPException(404, detail='invalid-province-code')
    response = asdict(province)

    districts = []
    if depth >= 2:
        for d in sorted(District.iter_by_province(pcode), key=attrgetter('code')):
            dd = asdict(d)
            if depth >= 3:
                dd['wards'] = tuple(asdict(w) for w in sorted(Ward.iter_by_district(d.code), key=attrgetter('code')))
            districts.append(dd)
    response['districts'] = tuple(districts)
    return response


@api_v1.get('/d/', response_model=list[DistrictResponse])
async def list_districts():
    return tuple(asdict(d) for d in sorted(District.iter_all(), key=attrgetter('code')))


@api_v1.get('/d/search/', response_model=SearchResults)
async def search_districts(q: str = SearchQuery, p: int | None = Query(None, title='Province code to filter')):
    if p is not None:
        try:
            pcode = ProvinceCode(p)
            items = tuple(filter(lambda x: x.province_code == pcode, District.search(q)))
        except ValueError:
            items = ()
    else:
        items = tuple(District.search(q))
    return _make_search_results(items)


@api_v1.get('/d/{code}', response_model=DistrictResponse)
async def get_district(
    code: int, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions', description='2: show wards')
):
    try:
        dcode = DistrictCode(code)
    except ValueError:
        raise HTTPException(404, detail='invalid-district-code')
    try:
        district = District.from_code(dcode)
    except (KeyError, ValueError, IndexError):
        raise HTTPException(404, detail='invalid-district-code')

    response = asdict(district)

    wards = []
    if depth >= 2:
        wards = [asdict(w) for w in sorted(Ward.iter_by_district(dcode), key=attrgetter('code'))]
    response['wards'] = tuple(wards)
    return response


@api_v1.get('/w/', response_model=list[WardResponse])
async def list_wards():
    return tuple(asdict(w) for w in sorted(Ward.iter_all(), key=attrgetter('code')))


@api_v1.get('/w/search/', response_model=SearchResults)
async def search_wards(
    q: str = SearchQuery,
    d: int | None = Query(None, title='District code to filter'),
    p: int | None = Query(None, title='Province code to filter, ignored if district is given'),
):
    items = tuple(Ward.search(q))
    if d is not None:
        try:
            dcode = DistrictCode(d)
            items = tuple(filter(lambda x: x.district_code == dcode, items))
        except ValueError:
            items = ()
    elif p is not None:
        try:
            pcode = ProvinceCode(p)
            dcodes = {dist.code for dist in District.iter_by_province(pcode)}
            items = tuple(filter(lambda x: x.district_code in dcodes, items))
        except ValueError:
            items = ()

    return _make_search_results(items)


@api_v1.get('/w/{code}', response_model=WardResponse)
async def get_ward(code: int):
    try:
        wcode = WardCode(code)
    except ValueError:
        raise HTTPException(404, detail='invalid-ward-code')
    try:
        ward = Ward.from_code(wcode)
    except (KeyError, ValueError, IndexError):
        raise HTTPException(404, detail='invalid-ward-code')
    return asdict(ward)


@api_v1.get('/version', response_model=VersionResponse)
async def get_version():
    return VersionResponse(data_version=__data_version__)
