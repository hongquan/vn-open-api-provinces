import os
from dataclasses import asdict
from operator import attrgetter

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi_problem.error import NotFoundProblem
from fastapi_problem.handler import add_exception_handler, new_exception_handler
from logbook import Logger
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province, ProvinceCode, Ward, WardCode

from . import __version__
from .schema_v2 import LegacyWardResponse, ProvinceResponse, WardResponse, WardWithLegacySource


api_v2 = FastAPI(title='Vietnam Provinces online API (2025)', version=__version__)
eh = new_exception_handler()
add_exception_handler(api_v2, eh)
logger = Logger(__name__)


class ProvinceNotExistError(NotFoundProblem):
    title = 'Province not exist'


class WardNotExistError(NotFoundProblem):
    title = 'Ward not exist'


@api_v2.get('/', response_model=tuple[ProvinceResponse, ...])
def show_all_divisions(request: Request, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions')):
    client_ip = request.client.host if request.client else None
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = filter(None, (s.strip() for s in env_value.split(',')))
        if not client_ip or client_ip in blacklist:
            raise HTTPException(429)
    if depth >= 2:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    return tuple(asdict(p) for p in sorted(Province.iter_all(), key=attrgetter('code')))


@api_v2.get('/p/')
async def list_provinces(search: str = '') -> tuple[ProvinceResponse, ...]:
    if search:
        provinces = Province.search(search)
    else:
        provinces = sorted(Province.iter_all(), key=attrgetter('code'))
    return tuple(ProvinceResponse(**asdict(p)) for p in provinces)


@api_v2.get('/p/{code}')
def get_province(
    code: int,
    depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions', description='2: show wards'),
) -> ProvinceResponse:
    try:
        pcode = ProvinceCode(code)
    except ValueError as e:
        raise ProvinceNotExistError(f'No province has code {code}') from e
    response = asdict(Province.from_code(pcode))
    if depth >= 2:
        wards = sorted(Ward.iter_by_province(pcode), key=attrgetter('code'))
        response['wards'] = tuple(w for w in wards)
    return ProvinceResponse(**response)


# FIXME: Failed to generate example response in API doc.
@api_v2.get('/w/', response_model=None)
async def list_wards(
    request: Request, province: int = 0, search: str = ''
) -> tuple[WardResponse, ...] | RedirectResponse:
    if province:
        try:
            province_code = ProvinceCode(province)
        except ValueError:
            # For invalid province code, redirect to new URL this this parameter stripped
            url = request.url.remove_query_params('province')
            logger.info('Redirect to {}', url)
            return RedirectResponse(url)
        wards = Ward.iter_by_province(province_code)
    else:
        wards = Ward.iter_all()
    if search:
        wards = Ward.search(search)
    return tuple(WardResponse(**asdict(p)) for p in sorted(wards, key=attrgetter('code')))


@api_v2.get('/w/{code}')
def get_ward(code: int) -> WardResponse:
    try:
        wcode = WardCode(code)
    except ValueError as e:
        raise WardNotExistError(f'No ward has code {code}') from e
    return WardResponse(**asdict(Ward.from_code(wcode)))


@api_v2.get('/w/from-legacy/', response_model=tuple[WardWithLegacySource, ...])
def lookup_from_legacy_ward(legacy_name: str = '', legacy_code: int = 0) -> tuple[WardWithLegacySource, ...]:
    """
    Lookup for new wards from pre-2025 name or pre-2025 code.
    """
    if not legacy_name and not legacy_code:
        return ()

    # Use the search_from_legacy classmethod from Ward as documented
    results = Ward.search_from_legacy(name=legacy_name, code=legacy_code)
    if not results:
        return ()

    # Convert WardWithLegacy objects to WardWithLegacySource dataclass instances
    response_items = []
    for result in results:
        ward_response = WardResponse(**asdict(result.ward))
        item = WardWithLegacySource(source_code=result.source_code, ward=ward_response)
        response_items.append(item)

    return tuple(response_items)


@api_v2.get(
    '/w/{code}/to-legacies/',
    response_model=tuple[LegacyWardResponse, ...],
    summary='Get legacy wards',
    description='Get pre-2025 wards that were merged to form this new ward.',
)
def get_legacy_wards(code: int) -> tuple[LegacyWardResponse, ...]:
    """
    Get pre-2025 wards that were merged to form this new ward.
    """
    try:
        # Get the new ward first
        ward = Ward.from_code(WardCode(code))
    except ValueError as e:
        raise WardNotExistError(f'No ward has code {code}') from e

    # Get legacy sources - these are LegacyWard namedtuples
    legacy_wards = ward.get_legacy_sources()
    if not legacy_wards:
        return ()

    # Convert legacy wards to LegacyWardResponse objects
    # Legacy wards are namedtuples with direct field access
    result = []
    for w in legacy_wards:
        legacy_ward_data = LegacyWardResponse(
            name=w.name,
            code=w.code,
            division_type=w.division_type,
            codename=w.codename,
            district_code=w.district_code,
            province_code=w.province_code,
        )
        result.append(legacy_ward_data)
    return tuple(result)
