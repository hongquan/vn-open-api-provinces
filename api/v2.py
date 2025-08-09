import os
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi_problem.error import NotFoundProblem
from fastapi_problem.handler import add_exception_handler, new_exception_handler
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province, ProvinceCode, Ward, WardCode

from .schema_v2 import ProvinceResponse, WardResponse


api_v2 = FastAPI()
eh = new_exception_handler()
add_exception_handler(api_v2, eh)


class ProvinceNotExistError(NotFoundProblem):
    title = 'Province not exist'


class WardNotExistError(NotFoundProblem):
    title = 'Ward not exist'


@api_v2.get('/', response_model=list[ProvinceResponse])
def show_all_divisions(request: Request, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions')):
    client_ip = request.client.host if request.client else None
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = filter(None, (s.strip() for s in env_value.split(',')))
        if not client_ip or client_ip in blacklist:
            raise HTTPException(429)
    if depth >= 2:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    return tuple(asdict(p) for p in Province.iter_all())


@api_v2.get('/p/')
async def list_provinces() -> tuple[ProvinceResponse, ...]:
    return tuple(ProvinceResponse(**asdict(p)) for p in Province.iter_all())


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
        wards = Ward.iter_by_province(pcode)
        response['wards'] = tuple(w for w in wards)
    return ProvinceResponse(**response)


@api_v2.get('/w/')
async def list_wards() -> tuple[WardResponse, ...]:
    return tuple(WardResponse(**asdict(p)) for p in Ward.iter_all())


@api_v2.get('/w/{code}')
def get_ward(code: int) -> WardResponse:
    try:
        wcode = WardCode(code)
    except ValueError as e:
        raise WardNotExistError(f'No ward has code {code}') from e
    return WardResponse(**asdict(Ward.from_code(wcode)))
