def test_create_item_type(client, auth_headers):
    item_type_data = {
        "item_type": "Switch"
    }

    response = client.post("/requisition/item-types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["item_type"] == item_type_data["item_type"]
    assert "id" in data


def test_create_item_type_duplicate(client, auth_headers):
    """
    Test creating a duplicate item type to ensure it raises an error.
    """
    item_type_data = {
        "item_type": "Switch"
    }

    # First request should succeed
    response = client.post("/requisition/item-types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 200

    # Second request with the same data should fail
    response = client.post("/requisition/item-types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "item type already exists or item type value is not string" in data["detail"].lower()


def test_create_item_type_blank_json(client, auth_headers):
    """
    Test creating an item type with a blank JSON object to ensure it raises an error.
    """
    # Sending an empty JSON object
    response = client.post("/requisition/item-types/", json={}, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["loc"] == ["body", "item_type"]
    assert data["detail"][0]["msg"] == "Field required"


def test_create_item_type_with_integer(client, auth_headers):
    """
    Test creating an item type with an integer value to ensure it raises an error.
    """
    # Sending an integer value for item_type
    item_type_data = {
        "item_type": 123
    }

    response = client.post("/requisition/item-types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()

