def test_create_item_type(client, auth_headers):
    item_type_data = {
        "item_type": "Switch"
    }

    # modified endpoint
    response = client.post("/requisition/items/types/", json=item_type_data, headers=auth_headers)
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
    response = client.post("/requisition/items/types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 200

    # Second request with the same data should fail
    response = client.post("/requisition/items/types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "item type already exists or item type value is not string" in data["detail"].lower()


def test_create_item_type_blank_json(client, auth_headers):
    """
    Test creating an item type with a blank JSON object to ensure it raises an error.
    """
    response = client.post("/requisition/items/types/", json={}, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["loc"] == ["body", "item_type"]
    assert data["detail"][0]["msg"] == "Field required"


def test_create_item_type_with_integer(client, auth_headers):
    """
    Test creating an item type with an integer value to ensure it raises an error.
    """
    item_type_data = {
        "item_type": 123
    }
    response = client.post("/requisition/items/types/", json=item_type_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_update_item_type(client, auth_headers):
    # Create an item type first.
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/items/types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    created = response.json()
    type_id = created["id"]

    # Update the item type to a new value.
    update_data = {"id": type_id, "item_type": "Router"}
    response_patch = client.patch(f"/requisition/items/types/{type_id}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 200
    updated = response_patch.json()
    assert updated["id"] == type_id
    assert updated["item_type"] == "Router"


def test_update_nonexistent_item_type(client, auth_headers):
    update_data = {"id": 9999, "item_type": "Nonexistent"}
    response = client.patch("/requisition/items/types/9999", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item type not found"


def test_update_item_type_duplicate(client, auth_headers):
    response1 = client.post("/requisition/items/types/", json={"item_type": "Switch"}, headers=auth_headers)
    assert response1.status_code == 200
    response2 = client.post("/requisition/items/types/", json={"item_type": "Router"}, headers=auth_headers)
    assert response2.status_code == 200
    type2 = response2.json()
    update_data = {"id": type2["id"], "item_type": "Switch"}
    response_patch = client.patch(f"/requisition/items/types/{type2['id']}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 400
    assert "item type already exists" in response_patch.json()["detail"].lower()


def test_update_item_type_with_integer(client, auth_headers):
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/items/types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    type_id = response.json()["id"]
    update_data = {"id": type_id, "item_type": 123}
    response_patch = client.patch(f"/requisition/items/types/{type_id}", json=update_data, headers=auth_headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_update_item_type_blank_json(client, auth_headers):
    create_data = {"item_type": "Switch"}
    response = client.post("/requisition/items/types/", json=create_data, headers=auth_headers)
    assert response.status_code == 200
    type_id = response.json()["id"]
    response_patch = client.patch(f"/requisition/items/types/{type_id}", json={}, headers=auth_headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    assert any("field required" in err["msg"].lower() for err in data["detail"])


def test_delete_item_type(client, auth_headers):
    create_data = {"item_type": "Switch"}
    response_create = client.post("/requisition/items/types/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    type_id = response_create.json()["id"]
    response_delete = client.delete(f"/requisition/items/types/{type_id}", headers=auth_headers)
    assert response_delete.status_code == 200
    data = response_delete.json()


def test_delete_nonexistent_item_type(client, auth_headers):
    response_delete = client.delete("/requisition/items/types/9999", headers=auth_headers)
    assert response_delete.status_code == 404
    data = response_delete.json()
    assert data["detail"] == "Item type not found"


def test_create_item_brand(client, auth_headers):
    brand_data = {"brand": "Samsung"}
    response = client.post("/requisition/items/brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == brand_data["brand"]
    assert "id" in data


def test_create_item_brand_duplicate(client, auth_headers):
    brand_data = {"brand": "Samsung"}
    response = client.post("/requisition/items/brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 200
    response_dup = client.post("/requisition/items/brands/", json=brand_data, headers=auth_headers)
    assert response_dup.status_code == 400
    data = response_dup.json()
    assert "detail" in data
    assert "item brand already exists" in data["detail"].lower()


def test_create_item_brand_blank_json(client, auth_headers):
    response = client.post("/requisition/items/brands/", json={}, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["loc"] == ["body", "brand"]
    assert "field required" in data["detail"][0]["msg"].lower()


def test_create_item_brand_with_integer(client, auth_headers):
    brand_data = {"brand": 123}
    response = client.post("/requisition/items/brands/", json=brand_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_update_item_brand(client, auth_headers):
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/items/brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    created = response_create.json()
    brand_id = created["id"]
    update_data = {"id": brand_id, "brand": "LG"}
    response_update = client.patch(f"/requisition/items/brands/{brand_id}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 200
    updated = response_update.json()
    assert updated["id"] == brand_id
    assert updated["brand"] == "LG"


def test_update_nonexistent_item_brand(client, auth_headers):
    update_data = {"id": 9999, "brand": "Nonexistent"}
    response = client.patch("/requisition/items/brands/9999", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item brand not found"


def test_update_item_brand_duplicate(client, auth_headers):
    response1 = client.post("/requisition/items/brands/", json={"brand": "Samsung"}, headers=auth_headers)
    assert response1.status_code == 200
    response2 = client.post("/requisition/items/brands/", json={"brand": "LG"}, headers=auth_headers)
    assert response2.status_code == 200
    brand2 = response2.json()
    update_data = {"id": brand2["id"], "brand": "Samsung"}
    response_update = client.patch(f"/requisition/items/brands/{brand2['id']}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 400
    data = response_update.json()
    assert "item brand already exists" in data["detail"].lower()


def test_update_item_brand_with_integer(client, auth_headers):
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/items/brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    brand_id = response_create.json()["id"]
    update_data = {"id": brand_id, "brand": 123}
    response_update = client.patch(f"/requisition/items/brands/{brand_id}", json=update_data, headers=auth_headers)
    assert response_update.status_code == 422
    data = response_update.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()


def test_delete_item_brand(client, auth_headers):
    create_data = {"brand": "Samsung"}
    response_create = client.post("/requisition/items/brands/", json=create_data, headers=auth_headers)
    assert response_create.status_code == 200
    brand_id = response_create.json()["id"]
    response_delete = client.delete(f"/requisition/items/brands/{brand_id}", headers=auth_headers)
    assert response_delete.status_code == 200
    data = response_delete.json()
    assert "message" in data
    assert f"{brand_id}" in data["message"]


def test_delete_nonexistent_item_brand(client, auth_headers):
    response_delete = client.delete("/requisition/items/brands/9999", headers=auth_headers)
    assert response_delete.status_code == 404
    data = response_delete.json()
    assert data["detail"] == "Item brand not found"


def test_create_item_success(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model X"
    }
    response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "Model X"
    assert data["type"] == created_item_type
    assert data["brand"] == created_item_brand
    assert "id" in data


def test_create_item_invalid_type(client, auth_headers, created_item_brand):
    item_data = {
        "type": 9999,
        "brand": created_item_brand,
        "model": "Model Y"
    }
    response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item type not found"


def test_create_item_invalid_brand(client, auth_headers, created_item_type):
    item_data = {
        "type": created_item_type,
        "brand": 9999,
        "model": "Model Z"
    }
    response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item brand not found"


def test_get_item(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Get"
    }
    create_response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    response = client.get(f"/requisition/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["model"] == "Model Get"


def test_list_items(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model List"
    }
    response_create = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert response_create.status_code == 200
    response = client.get("/requisition/items/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    matching_items = [item for item in data if item["model"] == "Model List"]
    assert len(matching_items) >= 1


def test_update_item_success(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Update Old"
    }
    create_response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    update_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Update New"
    }
    response = client.patch(f"/requisition/items/{item_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "Model Update New"
    assert data["id"] == item_id


def test_update_item_invalid_type(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Invalid Type"
    }
    create_response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    update_data = {
        "type": 9999,
        "brand": created_item_brand,
        "model": "Model Invalid Type"
    }
    response = client.patch(f"/requisition/items/{item_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item type not found"


def test_update_item_invalid_brand(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Invalid Brand"
    }
    create_response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    update_data = {
        "type": created_item_type,
        "brand": 9999,
        "model": "Model Invalid Brand"
    }
    response = client.patch(f"/requisition/items/{item_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item brand not found"


def test_delete_item(client, auth_headers, created_item_type, created_item_brand):
    item_data = {
        "type": created_item_type,
        "brand": created_item_brand,
        "model": "Model Delete"
    }
    create_response = client.post("/requisition/items/", json=item_data, headers=auth_headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    del_response = client.delete(f"/requisition/items/{item_id}", headers=auth_headers)
    assert del_response.status_code == 200
    assert f"Item {item_id} successfully deleted" in del_response.json()["message"]
    get_response = client.get(f"/requisition/items/{item_id}", headers=auth_headers)
    assert get_response.status_code == 404

