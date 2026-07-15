from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from src.database.models import User
from src.services.auth import create_email_token, create_password_reset_token
from tests.conftest import TestingSessionLocal, test_user

user_data = {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "12345678",
}


def test_signup(client, monkeypatch):
    monkeypatch.setattr("src.routers.auth.send_email", AsyncMock())
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_signup_duplicate(client, monkeypatch):
    monkeypatch.setattr("src.routers.auth.send_email", AsyncMock())
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Account already exists"


def test_login_unconfirmed(client):
    response = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Email not confirmed"


async def test_login(client):
    async with TestingSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalar_one_or_none()
        if user:
            user.confirmed = True
            await session.commit()

    response = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid password"


def test_login_wrong_email(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": user_data["password"]},
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid email"


def test_login_validation_error(client):
    response = client.post("/auth/login", json={"password": user_data["password"]})
    assert response.status_code == 422, response.text
    assert "detail" in response.json()


def test_refresh_success(client):
    login = client.post(
        "/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]},
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200, response.text
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_with_access_token(client, get_token):
    response = client.post(
        "/auth/refresh", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 401, response.text


def test_confirmed_email_already_confirmed(client):
    token = create_email_token({"sub": test_user["email"]})
    response = client.get(f"/auth/confirmed_email/{token}")
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Your email is already confirmed"


def test_confirmed_email_invalid_token(client):
    response = client.get("/auth/confirmed_email/invalid-token")
    assert response.status_code == 422, response.text


def test_request_email_already_confirmed(client):
    response = client.post("/auth/request_email", json={"email": test_user["email"]})
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Your email is already confirmed"


def test_request_email_not_found(client):
    response = client.post("/auth/request_email", json={"email": "nobody@example.com"})
    assert response.status_code == 200, response.text
    assert "message" in response.json()


def test_forgot_password(client, monkeypatch):
    monkeypatch.setattr("src.routers.auth.send_reset_password_email", AsyncMock())
    response = client.post("/auth/forgot_password", json={"email": user_data["email"]})
    assert response.status_code == 200, response.text
    assert "message" in response.json()


def test_forgot_password_nonexistent_email(client):
    response = client.post("/auth/forgot_password", json={"email": "ghost@example.com"})
    assert response.status_code == 200, response.text
    assert "message" in response.json()


def test_reset_password_form(client):
    token = create_password_reset_token(test_user["email"])
    response = client.get(f"/auth/reset_password/{token}")
    assert response.status_code == 200, response.text
    assert "text/html" in response.headers["content-type"]


def test_reset_password_success(client):
    token = create_password_reset_token(test_user["email"])
    response = client.post(
        f"/auth/reset_password/{token}", data={"password": "newpassword123"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Password updated successfully"


def test_reset_password_invalid_token(client):
    response = client.post(
        "/auth/reset_password/invalid-token", data={"password": "newpassword123"}
    )
    assert response.status_code == 422, response.text
