from uuid import uuid4

import pytest


@pytest.fixture
def user_route():
    return "/api/v1/users"


@pytest.fixture
def create_user_payload():
    return {
        "name": "Test",
        "email": "test@gmail.com",
        "password": "password",
    }


@pytest.fixture
def update_user_payload():
    return {"name": "Updated", "email": "updated@gmail.com"}


async def test_get_user_not_found(client, user_route):
    response = await client.get(f"{user_route}/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "User not found"}


async def test_get_user_invalid_id(client, user_route):
    response = await client.get(f"{user_route}/invalid-id")
    data, status_code = response.json(), response.status_code

    assert status_code == 422
    assert "detail" in data
    assert len(data["detail"]) == 1
    error = data["detail"][0]
    assert error["loc"] == ["path", "user_id"]
    assert error["type"] == "uuid_parsing"
    assert "Input should be a valid UUID" in error["msg"]


async def test_create_user_persistence(client, user_route, create_user_payload):
    create_response = await client.post(user_route, json=create_user_payload)
    created, status_code = create_response.json(), create_response.status_code

    assert status_code == 201

    get_response = await client.get(f"{user_route}/{created['id']}")
    fetched, status_code = get_response.json(), get_response.status_code

    assert status_code == 200
    assert created["name"] == fetched["name"]
    assert created["email"] == fetched["email"]


async def test_create_user_conflict(client, user_route, create_user_payload):
    await client.post(user_route, json=create_user_payload)
    response = await client.post(user_route, json=create_user_payload)
    data, status_code = response.json(), response.status_code

    assert status_code == 409
    assert data == {"detail": "User already exists"}


async def test_delete_user_not_found(client, user_route):
    response = await client.delete(f"{user_route}/{uuid4()}")
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "User not found"}


async def test_delete_user_successfully(client, user_route, create_user_payload):
    create_response = await client.post(user_route, json=create_user_payload)
    _id = create_response.json()["id"]
    delete_response = await client.delete(f"{user_route}/{_id}")

    assert delete_response.status_code == 204


async def test_patch_user_not_found(client, user_route, update_user_payload):
    response = await client.patch(f"{user_route}/{uuid4()}", json=update_user_payload)
    data, status_code = response.json(), response.status_code

    assert status_code == 404
    assert data == {"detail": "User not found"}


async def test_patch_all_user_data_successfully(
    client, user_route, create_user_payload, update_user_payload
):
    create_response = await client.post(user_route, json=create_user_payload)
    _id = create_response.json()["id"]
    patch_response = await client.patch(f"{user_route}/{_id}", json=update_user_payload)

    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == update_user_payload["name"]
    assert patch_response.json()["email"] == update_user_payload["email"]


async def test_patch_partial_user_data_successfully(
    client, user_route, create_user_payload, update_user_payload
):
    create_response = await client.post(user_route, json=create_user_payload)
    _id = create_response.json()["id"]

    update_user_payload["email"] = create_user_payload["email"]
    patch_response = await client.patch(f"{user_route}/{_id}", json=update_user_payload)

    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == update_user_payload["name"]
    assert patch_response.json()["email"] == create_user_payload["email"]

    del update_user_payload["email"]
    update_user_payload["name"] = "only name"
    patch_response = await client.patch(f"{user_route}/{_id}", json=update_user_payload)

    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == update_user_payload["name"]
    assert patch_response.json()["email"] == create_user_payload["email"]
