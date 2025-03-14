import pytest
import pytest_asyncio
from fastapi import FastAPI, Depends
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from starlette.status import HTTP_401_UNAUTHORIZED
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db_session
from backend.db.models import Guest
from backend.services.auth import create_access_token, get_token_from_cookie, validate_guest

app = FastAPI()

@app.get("/protected")
async def protected_route(
    token: str = Depends(get_token_from_cookie),
    guest=Depends(validate_guest)
):
    return {"success": True, "guest": {"guest_id": str(guest.guest_id), "email": guest.email}}

# Add a dependency override to use our test session
@pytest_asyncio.fixture
async def override_dependency(async_session):
    """Override the get_db_session dependency in FastAPI to use our test session."""
    async def get_test_session():
        yield async_session
    
    original_dependency = app.dependency_overrides.copy()
    app.dependency_overrides[get_db_session] = get_test_session
    yield
    app.dependency_overrides = original_dependency

@pytest_asyncio.fixture
async def seed_guest(async_session: AsyncSession):
    # 1) Delete tables (SQLite doesn't support TRUNCATE)
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()

    # 2) Insert a valid UUID
    my_uuid = "00000000-0000-0000-0000-000000000003"
    new_guest = Guest(
        guest_id=my_uuid,
        full_name="Chris Cheeseburger",
        email="chris.cheeseburger@oddmail.net"
    )
    async_session.add(new_guest)
    await async_session.commit()
    
    # Verify the guest was actually inserted
    result = await async_session.execute(
        text(f"SELECT * FROM guests WHERE guest_id = '{my_uuid}'")
    )
    guest = result.first()
    assert guest is not None, "Guest was not inserted correctly"
    
    yield my_uuid

@pytest_asyncio.fixture
async def client(override_dependency):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
async def test_cookie_missing_fails(client: AsyncClient):
    response = await client.get("/protected")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Missing access token"}

@pytest.mark.asyncio
async def test_cookie_present(client: AsyncClient, seed_guest):
    my_uuid = seed_guest
    token_value = create_access_token(my_uuid, "chris.cheeseburger@oddmail.net")
    client.cookies.set("access-token", token_value)
    
    response = await client.get("/protected")
    assert response.status_code == 200, f"Failed with response: {response.text}"
    
    data = response.json()
    assert data["guest"]["guest_id"] == str(my_uuid)
    assert data["guest"]["email"] == "chris.cheeseburger@oddmail.net"