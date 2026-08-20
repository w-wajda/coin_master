async def test_create_company(authenticated_client):
    response = await authenticated_client.post("/v2/companies/", json={"name": "Biedronka", "address": "Main St 1"})
    assert response.status_code == 201
    assert response.json()["name"] == "Biedronka"


async def test_get_company(authenticated_client, company):
    response = await authenticated_client.get(f"/v2/companies/{company.uuid}/")
    assert response.status_code == 200
    assert response.json()["uuid"] == str(company.uuid)


async def test_get_company_not_found(authenticated_client):
    response = await authenticated_client.get("/v2/companies/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404


async def test_get_company_list(authenticated_client, company):
    response = await authenticated_client.get("/v2/companies/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_update_company(authenticated_client, company):
    response = await authenticated_client.patch(
        f"/v2/companies/{company.uuid}/", json={"name": "Lidl", "address": "Other St 2"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Lidl"


async def test_update_company_not_found(authenticated_client):
    response = await authenticated_client.patch(
        "/v2/companies/00000000-0000-0000-0000-000000000000/", json={"name": "Lidl", "address": "Other St 2"}
    )
    assert response.status_code == 404


async def test_delete_company(authenticated_client, company):
    response = await authenticated_client.delete(f"/v2/companies/{company.uuid}/")
    assert response.status_code == 204


async def test_delete_company_not_found(authenticated_client):
    response = await authenticated_client.delete("/v2/companies/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404
