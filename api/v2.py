import os
from dataclasses import asdict
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province, ProvinceCode, Ward

from .schema_v2 import ProvinceResponse


api_v2 = FastAPI()


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


@api_v2.get('/p/', response_model=list[ProvinceResponse])
async def list_provinces():
    return tuple(asdict(p.value) for p in Province)


@api_v2.get('/p/{code}')
def get_province(
    code: int,
    depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions', description='2: show wards'),
) -> ProvinceResponse:
    try:
        pcode = ProvinceCode(code)
    except ValueError:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail='Invalid province code.')
    response = asdict(Province.from_code(pcode))
    if depth >= 2:
        wards = Ward.iter_by_province(pcode)
        response['wards'] = tuple(w for w in wards)
    return ProvinceResponse(**response)
