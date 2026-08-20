def _payload(**overrides):
    data = {
        "email_type": "WELCOME",
        "subject": "Hi",
        "text_content": "text",
        "html_content": "<p>html</p>",
        "is_active": True,
    }
    data.update(overrides)
    return data


async def test_create_email_template_requires_staff(authenticated_client):
    response = await authenticated_client.post("/v2/email_templates/", json=_payload())
    assert response.status_code == 403


async def test_create_email_template(staff_client):
    response = await staff_client.post("/v2/email_templates/", json=_payload())
    assert response.status_code == 201
    assert response.json()["subject"] == "Hi"


async def test_get_email_template(staff_client):
    create_response = await staff_client.post("/v2/email_templates/", json=_payload())
    template_uuid = create_response.json()["uuid"]

    response = await staff_client.get(f"/v2/email_templates/{template_uuid}/")
    assert response.status_code == 200
    assert response.json()["uuid"] == template_uuid


async def test_get_email_template_not_found(staff_client):
    response = await staff_client.get("/v2/email_templates/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404


async def test_get_email_template_list(staff_client):
    await staff_client.post("/v2/email_templates/", json=_payload())

    response = await staff_client.get("/v2/email_templates/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


async def test_update_email_template(staff_client):
    create_response = await staff_client.post("/v2/email_templates/", json=_payload())
    template_uuid = create_response.json()["uuid"]

    response = await staff_client.patch(f"/v2/email_templates/{template_uuid}/", json=_payload(subject="Updated"))
    assert response.status_code == 200
    assert response.json()["subject"] == "Updated"


async def test_update_email_template_not_found(staff_client):
    response = await staff_client.patch("/v2/email_templates/00000000-0000-0000-0000-000000000000/", json=_payload())
    assert response.status_code == 404


async def test_delete_email_template(staff_client):
    create_response = await staff_client.post("/v2/email_templates/", json=_payload())
    template_uuid = create_response.json()["uuid"]

    response = await staff_client.delete(f"/v2/email_templates/{template_uuid}/")
    assert response.status_code == 204


async def test_delete_email_template_not_found(staff_client):
    response = await staff_client.delete("/v2/email_templates/00000000-0000-0000-0000-000000000000/")
    assert response.status_code == 404
