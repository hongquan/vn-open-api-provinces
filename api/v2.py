import os
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict
from operator import attrgetter

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi_problem.error import NotFoundProblem
from fastapi_problem.handler import add_exception_handler, new_exception_handler
from logbook import Logger
from unidecode import unidecode
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province, ProvinceCode, Ward, WardCode

from . import __version__
from .schema_v2 import ProvinceResponse, WardResponse


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
    provinces = sorted(Province.iter_all(), key=attrgetter('code'))
    keywords = search.strip().lower().split()
    if keywords:
        logger.info('To filter by {}', keywords)
        provinces = filter_provinces_by_keywords(provinces, keywords)
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
    keywords = search.strip().lower().split()
    if keywords:
        logger.info('To filter by {}', keywords)
        # At this step, `wards` is an iterator, so when passing to filter_wards_by_keywords,
        # we need to convert it to a sequence, to allow iterating over it many times.
        wards = filter_wards_by_keywords(tuple(wards), keywords)
    return tuple(WardResponse(**asdict(p)) for p in sorted(wards, key=attrgetter('code')))


@api_v2.get('/w/{code}')
def get_ward(code: int) -> WardResponse:
    try:
        wcode = WardCode(code)
    except ValueError as e:
        raise WardNotExistError(f'No ward has code {code}') from e
    return WardResponse(**asdict(Ward.from_code(wcode)))


def filter_provinces_by_keywords(provinces: Sequence[Province], keywords: Iterable[str]):
    # Mapping of province code -> unaccent province
    unaccent_province_mapping = {p.code: unidecode(p.name).lower() for p in provinces}
    unaccent_keywords = tuple(unidecode(w) for w in keywords)

    def is_name_matched(province: Province):
        name = unaccent_province_mapping[province.code]
        return all(word in name for word in unaccent_keywords)

    return filter(is_name_matched, provinces)


def filter_wards_by_keywords(wards: Sequence[Ward], keywords: Iterable[str]) -> Iterator[Ward]:
    # Mapping of ward code -> unaccent name
    unaccent_ward_mapping = {w.code: unidecode(w.name).lower() for w in wards}
    unaccent_keywords = tuple(unidecode(w) for w in keywords)

    def is_name_matched(ward: Ward):
        name = unaccent_ward_mapping[ward.code]
        return all(word in name for word in unaccent_keywords)

    return filter(is_name_matched, wards)
