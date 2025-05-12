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

def test_update_item_type(client, auth_headers):
    # Create an item type first.
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/item-types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    created = response.json()
    type_id = created["id"]

    # Update the item type to a new value.
    update_data = {"id": type_id, "item_type": "Router"}
    response_patch = client.patch(f"/requisition/item-types/{type_id}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 200
    updated = response_patch.json()
    assert updated["id"] == type_id
    assert updated["item_type"] == "Router"


def test_update_nonexistent_item_type(client, auth_headers):
    # Attempt to update an item type that doesn't exist.
    update_data = {"id": 9999, "item_type": "Nonexistent"}
    response = client.patch("/requisition/item-types/9999", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item type not found"


def test_update_item_type_duplicate(client, auth_headers):
    # Create first item type "Switch".
    response1 = client.post("/requisition/item-types/", json={"item_type": "Switch"}, headers=auth_headers)
    assert response1.status_code == 200
    type1 = response1.json()

    # Create second item type "Router".
    response2 = client.post("/requisition/item-types/", json={"item_type": "Router"}, headers=auth_headers)
    assert response2.status_code == 200
    type2 = response2.json()

    # Attempt to update the second item type to "Switch" (which already exists).
    update_data = {"id": type2["id"], "item_type": "Switch"}
    response_patch = client.patch(f"/requisition/item-types/{type2['id']}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 400
    assert "item type already exists" in response_patch.json()["detail"].lower()


def test_update_item_type_with_integer(client, auth_headers):
    # Create a valid item type first.
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/item-types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    type_id = response.json()["id"]

    # Attempt to update the item type using an integer for the "item_type" field.
    update_data = {"id": type_id, "item_type": 123}
    response_patch = client.patch(f"/requisition/item-types/{type_id}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    # Ensure one of the validation errors mentions that the value should be a string
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_update_item_type_blank_json(client, auth_headers):
    # Create a valid item type first.
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/item-types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    type_id = response.json()["id"]

    # Attempt to update the item type with a blank JSON object.
    response_patch = client.patch(f"/requisition/item-types/{type_id}", json={}, headers=auth_headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    # Ensure the error indicates that the required field is missing.
    assert any("field required" in err["msg"].lower() for err in data["detail"])


def test_delete_item_type(client, auth_headers):
    """
    Test successfully deleting an existing item type.
    """
    # Create a valid item type first.
    create_data = {"item_type": "Switch"}
    response_create = client.post("/requisition/item-types/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    type_id = response_create.json()["id"]

    # Delete the item type.
    response_delete = client.delete(f"/requisition/item-types/{type_id}", headers=auth_headers)
    assert response_delete.status_code == 200
    data = response_delete.json()

def test_delete_nonexistent_item_type(client, auth_headers):
    """
    Test deleting an item type that doesn't exist.
    """
    response_delete = client.delete("/requisition/item-types/9999", headers=auth_headers)
    assert response_delete.status_code == 404
    data = response_delete.json()
    assert data["detail"] == "Item type not found"


def test_create_item_brand(client, auth_headers):
    brand_data = {"brand": "Samsung"}
    response = client.post("/requisition/item-brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == brand_data["brand"]
    assert "id" in data


def test_create_item_brand_duplicate(client, auth_headers):
    brand_data = {"brand": "Samsung"}
    # First creation should succeed.
    response = client.post("/requisition/item-brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 200

    # Duplicate creation should fail.
    response_dup = client.post("/requisition/item-brands/", json=brand_data, headers=auth_headers)
    assert response_dup.status_code == 400
    data = response_dup.json()
    assert "detail" in data
    assert "item brand already exists" in data["detail"].lower()


def test_create_item_brand_blank_json(client, auth_headers):
    response = client.post("/requisition/item-brands/", json={}, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Expect the missing field error for "brand".
    assert data["detail"][0]["loc"] == ["body", "brand"]
    assert "field required" in data["detail"][0]["msg"].lower()


def test_create_item_brand_with_integer(client, auth_headers):
    brand_data = {"brand": 123}
    response = client.post("/requisition/item-brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_update_item_brand(client, auth_headers):
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/item-brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    created = response_create.json()
    brand_id = created["id"]

    # Update the brand to a new value.
    update_data = {"id": brand_id, "brand": "LG"}
    response_update = client.patch(f"/requisition/item-brands/{brand_id}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 200
    updated = response_update.json()
    assert updated["id"] == brand_id
    assert updated["brand"] == "LG"


def test_update_nonexistent_item_brand(client, auth_headers):
    update_data = {"id": 9999, "brand": "Nonexistent"}
    response = client.patch("/requisition/item-brands/9999", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item brand not found"


def test_update_item_brand_duplicate(client, auth_headers):
    # Create two distinct brands.
    response1 = client.post("/requisition/item-brands/", json={"brand": "Samsung"}, headers=auth_headers)
    assert response1.status_code == 200
    brand1 = response1.json()

    response2 = client.post("/requisition/item-brands/", json={"brand": "LG"}, headers=auth_headers)
    assert response2.status_code == 200
    brand2 = response2.json()

    # Attempt to update the second brand to the duplicate value.
    update_data = {"id": brand2["id"], "brand": "Samsung"}
    response_update = client.patch(f"/requisition/item-brands/{brand2['id']}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 400
    data = response_update.json()
    assert "item brand already exists" in data["detail"].lower()


def test_update_item_brand_with_integer(client, auth_headers):
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/item-brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    brand_id = response_create.json()["id"]

    # Attempt to update using an integer for the "brand" field.
    update_data = {"id": brand_id, "brand": 123}
    response_update = client.patch(f"/requisition/item-brands/{brand_id}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 422
    data = response_update.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_delete_item_brand(client, auth_headers):
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/item-brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    brand_id = response_create.json()["id"]

    # Delete the brand.
    response_delete = client.delete(f"/requisition/item-brands/{brand_id}", headers=auth_headers)
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert "message" in data
    assert f"{brand_id}" in data["message"]


def test_delete_nonexistent_item_brand(client, auth_headers):
    response_delete = client.delete("/requisition/item-brands/9999", headers=auth_headers)
    assert response_delete.status_code == 404
    data = response_delete.json()
    assert data["detail"] == "Item brand not found"

