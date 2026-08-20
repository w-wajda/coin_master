async def test_create_receipt(authenticated_client, company):
    response = await authenticated_client.post(
        "/v2/receipts/",
        json={"amount": "10.50", "scan_file": "receipt.jpg"},
    )
    assert response.status_code == 201  # dowód błędu K1b: receipt_repository nie jest w kontenerze DI


async def test_delete_receipt(authenticated_client, receipt):
    response = await authenticated_client.delete(f"/v2/receipts/{receipt.uuid}/")
    assert response.status_code == 204  # dowód błędu K1b (a docelowo także K2: brak `return`)


async def test_get_receipt(authenticated_client, receipt):
    response = await authenticated_client.get(f"/v2/receipts/{receipt.uuid}/")
    assert response.status_code == 200
    assert response.json()["uuid"] == str(receipt.uuid)


async def test_get_receipt_not_found(authenticated_client):
    response = await authenticated_client.get("/v2/receipts/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404


async def test_get_receipt_list(authenticated_client, receipt):
    response = await authenticated_client.get("/v2/receipts/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_update_receipt(authenticated_client, receipt):
    response = await authenticated_client.patch(
        f"/v2/receipts/{receipt.uuid}/", json={"amount": "20.00", "scan_file": "updated.jpg"}
    )
    assert response.status_code == 200
    assert response.json()["scan_file"] == "updated.jpg"


async def test_update_receipt_not_found(authenticated_client):
    response = await authenticated_client.patch(
        "/v2/receipts/00000000-0000-0000-0000-000000000000/", json={"amount": "20.00", "scan_file": "updated.jpg"}
    )
    assert response.status_code == 404


async def test_create_item(authenticated_client, receipt):
    response = await authenticated_client.post(
        f"/v2/receipts/{receipt.uuid}/items/", json={"name": "Mleko", "price": "4.99"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Mleko"


async def test_create_item_receipt_not_found(authenticated_client):
    response = await authenticated_client.post(
        "/v2/receipts/00000000-0000-0000-0000-000000000000/items/", json={"name": "Mleko", "price": "4.99"}
    )
    assert response.status_code == 404


async def test_get_item_list(authenticated_client, receipt):
    await authenticated_client.post(f"/v2/receipts/{receipt.uuid}/items/", json={"name": "Mleko", "price": "4.99"})

    response = await authenticated_client.get(f"/v2/receipts/{receipt.uuid}/items/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_update_item(authenticated_client, receipt):
    create_response = await authenticated_client.post(
        f"/v2/receipts/{receipt.uuid}/items/", json={"name": "Mleko", "price": "4.99"}
    )
    item_uuid = create_response.json()["uuid"]

    response = await authenticated_client.patch(
        f"/v2/receipts/{receipt.uuid}/items/{item_uuid}/", json={"name": "Chleb", "price": "5.49"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Chleb"


async def test_update_item_not_found(authenticated_client, receipt):
    response = await authenticated_client.patch(
        f"/v2/receipts/{receipt.uuid}/items/00000000-0000-0000-0000-000000000000/",
        json={"name": "Chleb", "price": "5.49"},
    )
    assert response.status_code == 404


async def test_delete_item(authenticated_client, receipt):
    create_response = await authenticated_client.post(
        f"/v2/receipts/{receipt.uuid}/items/", json={"name": "Mleko", "price": "4.99"}
    )
    item_uuid = create_response.json()["uuid"]

    response = await authenticated_client.delete(f"/v2/receipts/{receipt.uuid}/items/{item_uuid}/")
    assert response.status_code == 204


async def test_delete_item_not_found(authenticated_client, receipt):
    response = await authenticated_client.delete(
        f"/v2/receipts/{receipt.uuid}/items/00000000-0000-0000-0000-000000000000/"
    )
    assert response.status_code == 404
