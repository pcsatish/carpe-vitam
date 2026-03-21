"""Integration tests for /api/v1/families endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_family(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/families", json={"name": "Smith Family"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Smith Family"
    assert "id" in data
    assert "created_by" in data


@pytest.mark.asyncio
async def test_list_families_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/families")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_families_shows_own_family(auth_client: AsyncClient):
    await auth_client.post("/api/v1/families", json={"name": "My Family"})
    resp = await auth_client.get("/api/v1/families")
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert "My Family" in names


@pytest.mark.asyncio
async def test_create_family_adds_creator_as_admin(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/families", json={"name": "Doe Family"})
    family_id = create_resp.json()["id"]

    members_resp = await auth_client.get(f"/api/v1/families/{family_id}/members")
    assert members_resp.status_code == 200
    members = members_resp.json()
    assert len(members) == 1
    assert members[0]["role"] == "admin"


@pytest.mark.asyncio
async def test_add_member(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/families", json={"name": "Jones Family"})
    family_id = create_resp.json()["id"]

    resp = await auth_client.post(f"/api/v1/families/{family_id}/members", json={
        "display_name": "Child One",
        "date_of_birth": "2010-05-15",
        "sex": "F",
        "role": "member",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["display_name"] == "Child One"
    assert data["role"] == "member"
    assert data["family_id"] == family_id


@pytest.mark.asyncio
async def test_list_members(auth_client: AsyncClient):
    create_resp = await auth_client.post("/api/v1/families", json={"name": "Brown Family"})
    family_id = create_resp.json()["id"]

    await auth_client.post(f"/api/v1/families/{family_id}/members", json={"display_name": "Grandpa"})

    resp = await auth_client.get(f"/api/v1/families/{family_id}/members")
    assert resp.status_code == 200
    names = [m["display_name"] for m in resp.json()]
    assert "Grandpa" in names


@pytest.mark.asyncio
async def test_non_member_cannot_list_members(auth_client: AsyncClient, client: AsyncClient):
    # Create family with auth_client
    create_resp = await auth_client.post("/api/v1/families", json={"name": "Private Family"})
    family_id = create_resp.json()["id"]

    # Register and log in a second user using the plain client
    await client.post("/api/v1/auth/register", json={
        "email": "other@example.com",
        "display_name": "Other User",
        "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "other@example.com",
        "password": "password123",
    })
    other_token = login_resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {other_token}"

    resp = await client.get(f"/api/v1/families/{family_id}/members")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_non_admin_cannot_add_member(auth_client: AsyncClient, client: AsyncClient):
    # Create family and add second user as MEMBER
    create_resp = await auth_client.post("/api/v1/families", json={"name": "Guarded Family"})
    family_id = create_resp.json()["id"]

    await client.post("/api/v1/auth/register", json={
        "email": "viewer@example.com",
        "display_name": "Viewer",
        "password": "password123",
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "viewer@example.com",
        "password": "password123",
    })
    viewer_token = login_resp.json()["access_token"]

    # Add this user as a member (not admin) via auth_client
    viewer_profile_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    viewer_user_id = viewer_profile_resp.json()["id"]
    await auth_client.post(f"/api/v1/families/{family_id}/members", json={
        "display_name": "Viewer",
        "role": "member",
        "user_id": viewer_user_id,
    })

    # Viewer tries to add another member — should be 403
    client.headers["Authorization"] = f"Bearer {viewer_token}"
    resp = await client.post(f"/api/v1/families/{family_id}/members", json={
        "display_name": "Intruder",
    })
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_family_requires_auth(client: AsyncClient):
    resp = await client.post("/api/v1/families", json={"name": "No Auth"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_family_validates_name(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/families", json={"name": ""})
    assert resp.status_code == 422
