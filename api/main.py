import os
import sys
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from logbook import Logger, StreamHandler
from logbook.more import ColorizedStderrHandler
from pydantic_settings import BaseSettings

from . import __version__
from .v1 import api_v1
from .v2 import api_v2


class Settings(BaseSettings):
    tracking: bool = False
    cdn_cache_interval: int = 30


logger = Logger(__name__)

if not os.getenv('VERCEL'):
    ColorizedStderrHandler().push_application()
else:
    StreamHandler(sys.stdout).push_application()


@asynccontextmanager
async def lifespan(app):
    from .search import repo

    logger.debug('To build search index')
    repo.build_index()
    logger.debug('Ready to search')
    yield


app = FastAPI(
    title='Vietnam Provinces online API',
    version=__version__,
    lifespan=lifespan,
    # redoc_url='/ref-doc/v1',
    # openapi_url='/api/v1/openapi.json',
)
settings = Settings()
app.mount('/api/v1', api_v1)
app.mount('/api/v2', api_v2)


@app.get('/api/', include_in_schema=False)
def redirect_api():
    return RedirectResponse(url='/api/v1/', status_code=HTTPStatus.TEMPORARY_REDIRECT)


@app.middleware('http')
async def guide_cdn_cache(request: Request, call_next):
    response = await call_next(request)
    # Ref: https://vercel.com/docs/edge-network/headers#cache-control-header
    response.headers['Cache-Control'] = f's-maxage={settings.cdn_cache_interval}, stale-while-revalidate'
    return response
