import os

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH, Province

from .schema_v2 import ProvinceResponse


api_v2 = APIRouter()


@api_v2.get('/', response_model=list[ProvinceResponse])
async def show_all_divisions(request: Request, depth: int = Query(1, ge=1, le=2, title='Show down to subdivisions')):
    client_ip = request.client.host if request.client else None
    if depth > 1:
        env_value = os.getenv('BLACKLISTED_CLIENTS', '')
        blacklist = filter(None, (s.strip() for s in env_value.split(',')))
        if not client_ip or client_ip in blacklist:
            raise HTTPException(429)
    if depth >= 2:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    return tuple(Province.iter_all())
