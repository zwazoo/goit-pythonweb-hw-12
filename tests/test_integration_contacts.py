from tests.conftest import test_user

contact_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+380991234567",
    "birthdate": "1990-05-15",
    "notes": "Test contact",
}

contact_id = None


def test_create_contact(client, get_token):
    global contact_id
    response = client.post(
        "/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["email"] == contact_data["email"]
    assert "id" in data
    contact_id = data["id"]


def test_create_duplicate_contact(client, get_token):
    response = client.post(
        "/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Email already exists"


def test_get_contacts(client, get_token):
    response = client.get(
        "/contacts/", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["email"] == contact_data["email"]


def test_get_contact_by_id(client, get_token):
    response = client.get(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == contact_data["first_name"]


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/contacts/99999", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Contact not found"


def test_search_contacts_by_name(client, get_token):
    response = client.get(
        "/contacts/?first_name=John",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 1
    assert data[0]["first_name"] == "John"


def test_update_contact(client, get_token):
    updated = {**contact_data, "first_name": "Jane"}
    response = client.put(
        f"/contacts/{contact_id}",
        json=updated,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["first_name"] == "Jane"


def test_update_contact_not_found(client, get_token):
    response = client.put(
        "/contacts/99999",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["id"] == contact_id


def test_delete_contact_not_found(client, get_token):
    response = client.delete(
        f"/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Contact not found"
