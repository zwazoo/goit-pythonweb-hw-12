from unittest.mock import patch, AsyncMock

from tests.conftest import test_user


def test_get_me(client, get_token):
    response = client.get("/users/me", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data
    assert "role" in data


def test_get_me_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == 401, response.text


@patch("src.services.users.cloudinary.uploader.upload")
def test_update_avatar_forbidden_for_user(mock_upload, client, get_token):
    mock_upload.return_value = {"secure_url": "http://example.com/avatar.jpg"}
    response = client.patch(
        "/users/avatar",
        headers={"Authorization": f"Bearer {get_token}"},
        files={"file": ("avatar.jpg", b"fake image content", "image/jpeg")},
    )
    assert response.status_code == 403, response.text
