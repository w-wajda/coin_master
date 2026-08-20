async def test_get_token_list(authenticated_client, token):
    response = await authenticated_client.get("/v2/tokens/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_create_token_success(client, user):
    response = await client.post("/v2/tokens/", json={"email": user.email, "password": "password"})
    assert response.status_code == 201
    assert "token" in response.json()


async def test_create_token_invalid_credentials(client, user):
    response = await client.post("/v2/tokens/", json={"email": user.email, "password": "wrong"})
    assert response.status_code == 400


async def test_revoke_token(authenticated_client, token):
    response = await authenticated_client.delete("/v2/tokens/revoke/")
    assert response.status_code == 204


async def test_delete_token(authenticated_client, token):
    response = await authenticated_client.delete(f"/v2/tokens/{token.uuid}/")
    assert response.status_code == 204
