import dataclasses
from itertools import groupby
from operator import attrgetter
from collections import deque
from typing import List

from logbook import Logger
from fastapi import FastAPI, APIRouter, Query
from fastapi.responses import FileResponse
from pydantic import BaseSettings

from vietnam_provinces import NESTED_DIVISIONS_JSON_PATH
from vietnam_provinces.enums import ProvinceEnum, DistrictEnum

from .schema import ProvinceResponse


class Settings(BaseSettings):
    tracking: bool = False


logger = Logger(__name__)
app = FastAPI(title='Vietnam Provinces online API')
api = APIRouter()
settings = Settings()


@api.get('/', response_model=List[ProvinceResponse])
async def show_all_provinces(depth: int = Query(1, ge=1, le=3, title='Show down to subdivisions')):
    if depth >= 3:
        return FileResponse(NESTED_DIVISIONS_JSON_PATH)
    if depth == 2:
        provinces = deque()
        for k, group in groupby(DistrictEnum, key=attrgetter('value.province_code')):
            p = dataclasses.asdict(ProvinceEnum[f'P_{k}'].value)
            p['districts'] = tuple(dataclasses.asdict(d.value) for d in group)
            provinces.append(p)
        return provinces
    return tuple(dataclasses.asdict(p.value) for p in ProvinceEnum)


app.include_router(api, prefix='/api')
