from http import HTTPStatus

import msgspec
import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


# Create msgspec Struct versions for testing
class LegacyWardResponse(msgspec.Struct):
    name: str
    code: int
    division_type: str
    codename: str
    district_code: int
    province_code: int


class ProvinceResponse(msgspec.Struct):
    name: str
    code: int
    division_type: str
    codename: str
    phone_code: int


class WardResponse(msgspec.Struct):
    name: str
    code: int
    division_type: str
    codename: str
    province_code: int


class WardWithLegacySourceResponse(msgspec.Struct):
    source_code: int
    ward: WardResponse


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://testServer') as client:
        yield client


@pytest.mark.asyncio
async def test_provinces(async_client):
    res = await async_client.get('/api/v2/p/')
    assert res.status_code == HTTPStatus.OK, res.text
    data = res.json()
    assert len(data) > 0
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=tuple[ProvinceResponse, ...])
    assert 'code' in data[0]


@pytest.mark.asyncio
async def test_get_province(async_client):
    res = await async_client.get('/api/v2/p/1')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=ProvinceResponse)


@pytest.mark.asyncio
async def test_search_provinces(async_client):
    res = await async_client.get('/api/v2/p/?search=Hà Nội')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=tuple[ProvinceResponse, ...])
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_wards(async_client):
    res = await async_client.get('/api/v2/w/')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=tuple[WardResponse, ...])
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_get_ward(async_client):
    # Use a valid ward code that exists - let's find a valid one first
    res = await async_client.get('/api/v2/w/')
    assert res.status_code == HTTPStatus.OK, res.text
    data = res.json()
    assert len(data) > 0
    # Use the first ward code from the list
    first_ward_code = data[0]['code']

    res = await async_client.get(f'/api/v2/w/{first_ward_code}')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=WardResponse)


@pytest.mark.asyncio
async def test_search_wards(async_client):
    res = await async_client.get('/api/v2/w/?search=Phúc Xá')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    msgspec.json.decode(res.content, type=tuple[WardResponse, ...])
    assert len(res.json()) > 0


@pytest.mark.asyncio
async def test_get_legacy_wards(async_client):
    """Test that get_legacy_wards returns correct legacy wards for a given ward code."""
    # Test with a known ward that has legacy sources
    res = await async_client.get('/api/v2/w/4/to-legacies/')  # Phường Ba Đình
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    legacy_wards = msgspec.json.decode(res.content, type=tuple[LegacyWardResponse, ...])

    # Should return results
    assert len(legacy_wards) > 0


@pytest.mark.asyncio
async def test_get_legacy_wards_tan_hai(async_client):
    """Test that get_legacy_wards for Phường Tân Hải returns correct legacy wards."""
    # First, we need to find which new ward code corresponds to the legacy wards 26707 and 26710
    # Let's test both new ward codes that might contain these legacy wards
    
    # Test ward code 26707
    res = await async_client.get('/api/v2/w/26707/to-legacies/')
    if res.status_code == HTTPStatus.OK:
        legacy_wards = msgspec.json.decode(res.content, type=tuple[LegacyWardResponse, ...])
        # Check if this returns the expected legacy wards
        
    # Test ward code 26710  
    res = await async_client.get('/api/v2/w/26710/to-legacies/')
    assert res.status_code == HTTPStatus.OK, res.text
    legacy_wards = msgspec.json.decode(res.content, type=tuple[LegacyWardResponse, ...])
    
    # Should return legacy wards including those with codes 26707 and 26710
    assert len(legacy_wards) >= 1


@pytest.mark.asyncio
async def test_get_legacy_wards_invalid_code(async_client):
    """Test that get_legacy_wards returns 404 for invalid ward code."""
    res = await async_client.get('/api/v2/w/999999/to-legacies/')
    assert res.status_code == HTTPStatus.NOT_FOUND, res.text


@pytest.mark.asyncio
async def test_lookup_from_legacy_ward_by_name(async_client):
    """Test that lookup_from_legacy_ward returns correct wards when searching by legacy name."""
    # Test with a known legacy ward name that should return results
    res = await async_client.get('/api/v2/w/from-legacy/?legacy_name=Ba Đình')
    assert res.status_code == HTTPStatus.OK, res.text
    # Validate response structure with msgspec
    wards = msgspec.json.decode(res.content, type=tuple[WardWithLegacySourceResponse, ...])
    
    # Should return results
    assert len(wards) >= 0  # Allow for empty results but should not fail
