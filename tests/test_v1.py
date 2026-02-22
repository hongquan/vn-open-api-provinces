from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testServer') as client:
        yield client


@pytest.mark.asyncio
async def test_provinces(async_client):
    res = await async_client.get('/api/v1/p/')
    assert res.status_code == HTTPStatus.OK, res.text
    data = res.json()
    assert len(data) > 0
    assert 'code' in data[0]


@pytest.mark.asyncio
async def test_get_province(async_client):
    res = await async_client.get('/api/v1/p/1')
    assert res.status_code == HTTPStatus.OK, res.text
    assert res.json()['code'] == 1


@pytest.mark.asyncio
async def test_search_provinces(async_client):
    res = await async_client.get('/api/v1/p/search/?q=Hà Nội')
    assert res.status_code == HTTPStatus.OK, res.text
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_districts(async_client):
    res = await async_client.get('/api/v1/d/')
    assert res.status_code == HTTPStatus.OK, res.text
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_get_district(async_client):
    res = await async_client.get('/api/v1/d/1')
    assert res.status_code == HTTPStatus.OK, res.text
    assert res.json()['code'] == 1


@pytest.mark.asyncio
async def test_search_districts(async_client):
    res = await async_client.get('/api/v1/d/search/?q=Hoàn Kiếm')
    assert res.status_code == HTTPStatus.OK, res.text
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_wards(async_client):
    res = await async_client.get('/api/v1/w/')
    assert res.status_code == HTTPStatus.OK, res.text
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_get_ward(async_client):
    res = await async_client.get('/api/v1/w/1')
    assert res.status_code == HTTPStatus.OK, res.text
    assert res.json()['code'] == 1


@pytest.mark.asyncio
async def test_search_wards(async_client):
    res = await async_client.get('/api/v1/w/search/?q=Phúc Xá')
    assert res.status_code == HTTPStatus.OK, res.text
    assert len(res.json()) > 0
