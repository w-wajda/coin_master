import sqlalchemy as sa

from app.domain.users.email_token import EmailToken


async def test_reset_password_flow(client, session_maker, user):
    response = await client.post("/v2/users/reset-password/", json={"email": user.email})
    assert response.status_code == 204

    async with session_maker() as session:
        result = await session.execute(sa.select(EmailToken).filter_by(user_id=user.id))
        email_token = result.scalar_one()
    assert email_token.type == EmailToken.TYPES.password_reset

    confirm_response = await client.post(
        "/v2/users/reset-password/confirm/",
        json={"token": email_token.token, "password1": "newpassword123", "password2": "newpassword123"},
    )
    assert confirm_response.status_code == 204

    old_password_login = await client.post("/v2/tokens/", json={"email": user.email, "password": "password"})
    assert old_password_login.status_code == 400

    new_password_login = await client.post(
        "/v2/tokens/", json={"email": user.email, "password": "newpassword123"}
    )
    assert new_password_login.status_code == 201


async def test_reset_password_unknown_email_returns_204(client):
    response = await client.post("/v2/users/reset-password/", json={"email": "unknown@example.com"})
    assert response.status_code == 204


async def test_create_user_registers_and_logs_in(client):
    response = await client.post("/v2/users/", json={"email": "newuser@example.com", "password": "password123"})
    assert response.status_code == 201
    assert "token" in response.json()


async def test_create_user_duplicate_email(client, user):
    response = await client.post("/v2/users/", json={"email": user.email, "password": "password123"})
    assert response.status_code == 400


async def test_get_user(authenticated_client, user):
    response = await authenticated_client.get("/v2/users/me/")
    assert response.status_code == 200
    assert response.json()["uuid"] == str(user.uuid)


async def test_patch_user(authenticated_client):
    response = await authenticated_client.patch("/v2/users/me/", json={"email": "changed@example.com"})
    assert response.status_code == 200
    assert response.json()["email"] == "changed@example.com"


async def test_change_password(authenticated_client):
    response = await authenticated_client.post(
        "/v2/users/change-password/",
        json={"old_password": "password", "password1": "newpassword123", "password2": "newpassword123"},
    )
    assert response.status_code == 204


async def test_change_password_invalid_old_password(authenticated_client):
    response = await authenticated_client.post(
        "/v2/users/change-password/",
        json={"old_password": "wrongpassword", "password1": "newpassword123", "password2": "newpassword123"},
    )
    assert response.status_code == 400
