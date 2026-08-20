async def test_create_tag(authenticated_client):
    response = await authenticated_client.post("/v2/tags/", json={"name": "Groceries"})
    assert response.status_code == 201
    assert response.json()["name"] == "Groceries"


async def test_get_tag(authenticated_client):
    create_response = await authenticated_client.post("/v2/tags/", json={"name": "Travel"})
    tag_uuid = create_response.json()["uuid"]

    response = await authenticated_client.get(f"/v2/tags/{tag_uuid}/")
    assert response.status_code == 200
    assert response.json()["uuid"] == tag_uuid


async def test_get_tag_not_found(authenticated_client):
    response = await authenticated_client.get("/v2/tags/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404


async def test_get_tag_list(authenticated_client):
    await authenticated_client.post("/v2/tags/", json={"name": "Groceries"})

    response = await authenticated_client.get("/v2/tags/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_update_tag(authenticated_client):
    create_response = await authenticated_client.post("/v2/tags/", json={"name": "Groceries"})
    tag_uuid = create_response.json()["uuid"]

    response = await authenticated_client.patch(f"/v2/tags/{tag_uuid}/", json={"name": "Food"})
    assert response.status_code == 200
    assert response.json()["name"] == "Food"


async def test_update_tag_not_found(authenticated_client):
    response = await authenticated_client.patch("/v2/tags/00000000-0000-0000-0000-000000000000/", json={"name": "Food"})
    assert response.status_code == 404


async def test_delete_tag(authenticated_client):
    create_response = await authenticated_client.post("/v2/tags/", json={"name": "Groceries"})
    tag_uuid = create_response.json()["uuid"]

    response = await authenticated_client.delete(f"/v2/tags/{tag_uuid}/")
    assert response.status_code == 204


async def test_delete_tag_not_found(authenticated_client):
    response = await authenticated_client.delete("/v2/tags/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404
