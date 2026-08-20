async def test_create_receipt(authenticated_client, company):
    response = await authenticated_client.post(
        "/v2/receipts/",
        json={"amount": "10.50", "scan_file": "receipt.jpg"},
    )
    assert response.status_code == 201  # dowód błędu K1b: receipt_repository nie jest w kontenerze DI


async def test_delete_receipt(authenticated_client, receipt):
    response = await authenticated_client.delete(f"/v2/receipts/{receipt.uuid}/")
    assert response.status_code == 204  # dowód błędu K1b (a docelowo także K2: brak `return`)
