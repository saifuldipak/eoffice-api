from src.models import RequisitionUnit, UserAction

def test_item_type_create(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    item_type_data = {
        "item_type": "Switch"
    }
    response = client.post("/requisitions/items/types/", json=item_type_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["item_type"] == item_type_data["item_type"]
    assert "id" in data

def test_item_type_create_wrong_permission(client, auth_headers):
    headers = auth_headers(UserAction.MANAGE_TICKET)
    item_type_data = {
        "item_type": "Switch"
    }
    response = client.post("/requisitions/items/types/", json=item_type_data, headers=headers)
    assert response.status_code == 403
    
def test_item_type_create_duplicate(client, auth_headers):
    """
    Test creating a duplicate item type to ensure it raises an error.
    """
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    item_type_data = {
        "item_type": "Switch"
    }
    # First request should succeed
    response = client.post("/requisitions/items/types/", json=item_type_data, headers=headers)
    assert response.status_code == 200
    # Second request with the same data should fail
    response = client.post("/requisitions/items/types/", json=item_type_data, headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "item type already exists or item type value is not string" in data["detail"].lower()

def test_item_type_create_blank_json(client, auth_headers):
    """
    Test creating an item type with a blank JSON object to ensure it raises an error.
    """
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response = client.post("/requisitions/items/types/", json={}, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["loc"] == ["body", "item_type"]
    assert data["detail"][0]["msg"] == "Field required"

def test_item_type_create_with_integer(client, auth_headers):
    """
    Test creating an item type with an integer value to ensure it raises an error.
    """
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    item_type_data = {
        "item_type": 123
    }
    response = client.post("/requisitions/items/types/", json=item_type_data, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()

def test_item_type_update(client, auth_headers):
    headers = auth_headers(UserAction.MANAGE_TICKET)
    type_id = 1
    update_data = {"id": type_id, "item_type": "Router"}
    response_patch = client.patch(f"/requisitions/items/types/{type_id}", json=update_data, headers=headers)
    assert response_patch.status_code == 403

def test_item_type_update_wrong_permission(client, auth_headers):
    headers_wrong = auth_headers(UserAction.MANAGE_TICKET)
    type_id = 1
    update_data = {"id": type_id, "item_type": "Updated Unauthorized"}
    response_patch = client.patch(f"/requisitions/items/types/{type_id}", json=update_data, headers=headers_wrong)
    assert response_patch.status_code == 403
    data = response_patch.json()
    assert "detail" in data

def test_item_type_update_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    update_data = {"id": 9999, "item_type": "Nonexistent"}
    response = client.patch("/requisitions/items/types/9999", json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item type not found"

def test_item_type_update_duplicate(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response1 = client.post("/requisitions/items/types/", json={"item_type": "Switch"}, headers=headers)
    assert response1.status_code == 200
    response2 = client.post("/requisitions/items/types/", json={"item_type": "Router"}, headers=headers)
    assert response2.status_code == 200
    type2 = response2.json()
    update_data = {"id": type2["id"], "item_type": "Switch"}
    response_patch = client.patch(f"/requisitions/items/types/{type2['id']}", json=update_data, headers=headers)
    assert response_patch.status_code == 400
    assert "item type already exists" in response_patch.json()["detail"].lower()

def test_item_type_update_with_integer(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    create_data = {"item_type": "Switch"}
    response = client.post("/requisitions/items/types/", json=create_data, headers=headers)
    assert response.status_code == 200
    type_id = response.json()["id"]
    update_data = {"id": type_id, "item_type": 123}
    response_patch = client.patch(f"/requisitions/items/types/{type_id}", json=update_data, headers=headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()

def test_item_type_update_blank_json(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    create_data = {"item_type": "Switch"}
    response = client.post("/requisitions/items/types/", json=create_data, headers=headers)
    assert response.status_code == 200
    type_id = response.json()["id"]
    response_patch = client.patch(f"/requisitions/items/types/{type_id}", json={}, headers=headers)
    assert response_patch.status_code == 422
    data = response_patch.json()
    assert "detail" in data
    assert any("field required" in err["msg"].lower() for err in data["detail"])

def test_item_type_delete(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    create_data = {"item_type": "Switch"}
    response_create = client.post("/requisitions/items/types/", json=create_data, headers=headers)
    assert response_create.status_code == 200
    type_id = response_create.json()["id"]
    response_delete = client.delete(f"/requisitions/items/types/{type_id}", headers=headers)
    assert response_delete.status_code == 200
    data = response_delete.json()

def test_item_type_delete_wrong_permission(client, auth_headers):
    headers = auth_headers(UserAction.MANAGE_TICKET)
    response_delete = client.delete(f"/requisitions/items/types/999", headers=headers)
    assert response_delete.status_code == 403

def test_item_type_delete_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response_delete = client.delete("/requisitions/items/types/9999", headers=headers)
    assert response_delete.status_code == 404
    data = response_delete.json()
    assert data["detail"] == "Item type not found"

def test_item_type_get_by_id(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create an item type first.
    create_data = {"item_type": "Switch"}
    create_response = client.post("/requisitions/items/types/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    type_id = create_response.json()["id"]

    # Retrieve the created item type by its id.
    get_response = client.get(f"/requisitions/items/types/{type_id}", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == type_id
    assert data["item_type"] == create_data["item_type"]

def test_item_type_get_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    get_response = client.get(f"/requisitions/items/types/999", headers=wrong_headers)
    assert get_response.status_code == 403

def test_item_type_list(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create multiple item types.
    types = [{"item_type": "Switch"}, {"item_type": "Router"}]
    for t in types:
        response = client.post("/requisitions/items/types/", json=t, headers=headers)
        assert response.status_code == 200

    # List all item types.
    list_response = client.get("/requisitions/items/types/", headers=headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert isinstance(data, list)
    # Verify that both created item types are in the returned list.
    returned_types = [item["item_type"] for item in data]
    for t in types:
        assert t["item_type"] in returned_types

def test_item_type_list_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    list_response = client.get("/requisitions/items/types/", headers=wrong_headers)
    assert list_response.status_code == 403

def test_item_brand_create(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    brand_data = {"brand": "Samsung"}
    response = client.post("/requisitions/items/brands/", json=brand_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == brand_data["brand"]
    assert "id" in data

def test_item_brand_create_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    brand_data = {"brand": "Samsung"}
    response = client.post("/requisitions/items/brands/", json=brand_data, headers=wrong_headers)
    assert response.status_code == 403

def test_item_brand_create_duplicate(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    brand_data = {"brand": "Samsung"}
    # First creation should succeed.
    response1 = client.post("/requisitions/items/brands/", json=brand_data, headers=headers)
    assert response1.status_code == 200
    # Duplicate creation should fail.
    response2 = client.post("/requisitions/items/brands/", json=brand_data, headers=headers)
    assert response2.status_code == 400
    data = response2.json()
    assert "detail" in data
    assert "item brand already exists" in data["detail"].lower()

def test_item_brand_create_blank_json(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response = client.post("/requisitions/items/brands/", json={}, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Check that the error indicates a missing 'brand' field.
    assert data["detail"][0]["loc"] == ["body", "brand"]
    assert data["detail"][0]["msg"] == "Field required"

def test_item_brand_create_with_integer(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    brand_data = {"brand": 123}
    response = client.post("/requisitions/items/brands/", json=brand_data, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()

def test_item_brand_update(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    create_response = client.post("/requisitions/items/brands/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    brand_id = create_response.json()["id"]
    # Update the brand.
    update_data = {"id": brand_id, "brand": "LG"}
    update_response = client.patch(f"/requisitions/items/brands/{brand_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["brand"] == "LG"

def test_item_brand_update_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    update_data = {"id": 1, "brand": "LG"}
    update_response = client.patch(f"/requisitions/items/brands/1", json=update_data, headers=wrong_headers)
    assert update_response.status_code == 403

def test_item_brand_update_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    update_data = {"id": 9999, "brand": "Nonexistent"}
    response = client.patch("/requisitions/items/brands/9999", json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item brand not found"

def test_item_brand_update_with_integer(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand.
    create_data = {"brand": "Samsung"}
    create_response = client.post("/requisitions/items/brands/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    brand_id = create_response.json()["id"]
    # Attempt to update with an integer value.
    update_data = {"id": brand_id, "brand": 123}
    response = client.patch(f"/requisitions/items/brands/{brand_id}", json=update_data, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "input should be a valid string" in data["detail"][0]["msg"].lower()

def test_item_brand_update_blank_json(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    create_response = client.post("/requisitions/items/brands/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    brand_id = create_response.json()["id"]
    # Attempt to update with a blank JSON.
    response = client.patch(f"/requisitions/items/brands/{brand_id}", json={}, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("field required" in err["msg"].lower() for err in data["detail"])

def test_item_brand_update_duplicate(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand "Samsung"
    response1 = client.post("/requisitions/items/brands/", json={"brand": "Samsung"}, headers=headers)
    assert response1.status_code == 200
    # Create another brand "LG"
    response2 = client.post("/requisitions/items/brands/", json={"brand": "LG"}, headers=headers)
    assert response2.status_code == 200
    brand2 = response2.json()
    # Attempt to update brand2 to have "Samsung", which already exists
    update_data = {"id": brand2["id"], "brand": "Samsung"}
    response_patch = client.patch(f"/requisitions/items/brands/{brand2['id']}", json=update_data, headers=headers)
    assert response_patch.status_code == 400
    data = response_patch.json()
    assert "item brand already exists" in data["detail"].lower()

def test_item_brand_delete(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand.
    create_data = {"brand": "Samsung"}
    create_response = client.post("/requisitions/items/brands/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    brand_id = create_response.json()["id"]
    # Delete the brand.
    delete_response = client.delete(f"/requisitions/items/brands/{brand_id}", headers=headers)
    assert delete_response.status_code == 200

def test_item_brand_delete_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    delete_response = client.delete(f"/requisitions/items/brands/999", headers=wrong_headers)
    assert delete_response.status_code == 403

def test_item_brand_delete_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response = client.delete("/requisitions/items/brands/9999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Item brand not found"

def test_item_brand_get_by_id(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create a brand first.
    create_data = {"brand": "Samsung"}
    create_response = client.post("/requisitions/items/brands/", json=create_data, headers=headers)
    assert create_response.status_code == 200
    brand_id = create_response.json()["id"]
    # Retrieve the brand by its id.
    get_response = client.get(f"/requisitions/items/brands/{brand_id}", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == brand_id
    assert data["brand"] == create_data["brand"]

def test_item_brand_get_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    # Attempt to retrieve a brand with the wrong permission.
    response = client.get("/requisitions/items/brands/1", headers=wrong_headers)
    assert response.status_code == 403

def test_item_brand_list(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    # Create multiple brands.
    brands = [{"brand": "Samsung"}, {"brand": "LG"}, {"brand": "Sony"}]
    for brand in brands:
        resp = client.post("/requisitions/items/brands/", json=brand, headers=headers)
        assert resp.status_code == 200
    # Retrieve the list of brands.
    list_response = client.get("/requisitions/items/brands/", headers=headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert isinstance(data, list)
    retrieved_brands = [item["brand"] for item in data]
    for brand in brands:
        assert brand["brand"] in retrieved_brands

def test_item_brand_list_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    response = client.get("/requisitions/items/brands/", headers=wrong_headers)
    assert response.status_code == 403

def test_item_create(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Test Model"
    }
    response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == item_data["type"]
    assert data["brand"] == item_data["brand"]
    assert data["model"] == item_data["model"]
    assert "id" in data

def test_item_create_wrong_permission(client, auth_headers, created_item_type, created_item_brand):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    item_data = {
        "type": 10,
        "brand": 11,
        "model": "Test Model"
    }
    response = client.post("/requisitions/items/", json=item_data, headers=wrong_headers)
    assert response.status_code == 403

def test_item_create_invalid_type(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    item_data = {
        "type": 9999,
        "brand": None,
        "model": "Test Model"
    }
    response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response.status_code == 404
    assert "Item type not found" in response.json()["detail"]

def test_item_create_invalid_brand(client, auth_headers, created_item_type):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    
    item_data = {
        "type": type_id,
        "brand": 9999,
        "model": "Test Model"
    }
    response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response.status_code == 404
    assert "Item brand not found" in response.json()["detail"]

def test_item_create_duplicate_model(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Duplicate Model"
    }
    # First creation should succeed
    response1 = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response1.status_code == 200
    
    # Second creation with same model should fail
    response2 = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response2.status_code == 400
    assert "model already exists" in response2.json()["detail"]

def test_item_create_without_brand(client, auth_headers, created_item_type):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    
    item_data = {
        "type": type_id,
        "brand": None,
        "model": "No Brand Model"
    }
    response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == item_data["type"]
    assert data["brand"] is None
    assert data["model"] == item_data["model"]

def test_item_get_by_id(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create an item first
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Get Test Model"
    }
    create_response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Get the item by ID
    get_response = client.get(f"/requisitions/items/{item_id}", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == item_id
    assert data["type"] == item_data["type"]
    assert data["brand"] == item_data["brand"]
    assert data["model"] == item_data["model"]

def test_item_get_by_id_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    response = client.get("/requisitions/items/1", headers=wrong_headers)
    assert response.status_code == 403

def test_item_get_by_id_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response = client.get("/requisitions/items/9999", headers=headers)
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]

def test_item_list(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create multiple items
    items = [
        {"type": type_id, "brand": brand_id, "model": "List Model 1"},
        {"type": type_id, "brand": brand_id, "model": "List Model 2"}
    ]
    for item in items:
        response = client.post("/requisitions/items/", json=item, headers=headers)
        assert response.status_code == 200
    
    # List all items
    list_response = client.get("/requisitions/items/", headers=headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert isinstance(data, list)
    # Verify created items are in the list
    returned_models = [item["model"] for item in data]
    for item in items:
        assert item["model"] in returned_models

def test_item_list_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    response = client.get("/requisitions/items/", headers=wrong_headers)
    assert response.status_code == 403

def test_item_update(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create an item first
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Original Model"
    }
    create_response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Update the item
    update_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Updated Model"
    }
    update_response = client.patch(f"/requisitions/items/{item_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["model"] == "Updated Model"

def test_item_update_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    update_data = {
        "type": 1,
        "brand": 1,
        "model": "Updated Model"
    }
    response = client.patch("/requisitions/items/1", json=update_data, headers=wrong_headers)
    assert response.status_code == 403

def test_item_update_nonexistent(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    update_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Updated Model"
    }
    response = client.patch("/requisitions/items/9999", json=update_data, headers=headers)
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]

def test_item_update_invalid_type(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create an item first
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Test Model"
    }
    create_response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Try to update with invalid type
    update_data = {
        "type": 9999,
        "brand": brand_id,
        "model": "Updated Model"
    }
    response = client.patch(f"/requisitions/items/{item_id}", json=update_data, headers=headers)
    assert response.status_code == 404
    assert "Item type not found" in response.json()["detail"]

def test_item_update_invalid_brand(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create an item first
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Test Model"
    }
    create_response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Try to update with invalid brand
    update_data = {
        "type": type_id,
        "brand": 9999,
        "model": "Updated Model"
    }
    response = client.patch(f"/requisitions/items/{item_id}", json=update_data, headers=headers)
    assert response.status_code == 404
    assert "Item brand not found" in response.json()["detail"]

def test_item_update_duplicate_model(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create first item
    item1_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Existing Model"
    }
    response1 = client.post("/requisitions/items/", json=item1_data, headers=headers)
    assert response1.status_code == 200
    
    # Create second item
    item2_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Another Model"
    }
    response2 = client.post("/requisitions/items/", json=item2_data, headers=headers)
    assert response2.status_code == 200
    item2_id = response2.json()["id"]
    
    # Try to update second item with first item's model
    update_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Existing Model"
    }
    response = client.patch(f"/requisitions/items/{item2_id}", json=update_data, headers=headers)
    assert response.status_code == 400
    assert "model already exists" in response.json()["detail"]

def test_item_delete(client, auth_headers, created_item_type, created_item_brand):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    
    # Create an item first
    item_data = {
        "type": type_id,
        "brand": brand_id,
        "model": "Delete Test Model"
    }
    create_response = client.post("/requisitions/items/", json=item_data, headers=headers)
    assert create_response.status_code == 200
    item_id = create_response.json()["id"]
    
    # Delete the item
    delete_response = client.delete(f"/requisitions/items/{item_id}", headers=headers)
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert f"Item with Id {item_id} deleted successfully" in data["message"]

def test_item_delete_wrong_permission(client, auth_headers):
    wrong_headers = auth_headers(UserAction.MANAGE_TICKET)
    response = client.delete("/requisitions/items/1", headers=wrong_headers)
    assert response.status_code == 403

def test_item_delete_nonexistent(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    response = client.delete("/requisitions/items/9999", headers=headers)
    assert response.status_code == 404
    assert "Item with Id" in response.json()["detail"]

def test_requisition_create(client, auth_headers, created_item_type, created_item_brand, created_item, requisition_data):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    model_list = ["Model A", "Model B", "Model C"]
    requisition_data_list = []
    for model in model_list:
        item_id = created_item(headers, type_id, brand_id, model)
        requisition_item = requisition_data.copy()
        requisition_item["item_id"] = item_id
        requisition_data_list.append(requisition_item)
    
    response = client.post("/requisitions/", json=requisition_data_list, headers=headers)
    assert response.status_code == 200
    response_data_list = response.json()
    assert isinstance(response_data_list, list)
    assert len(response_data_list) == len(requisition_data_list)

    for i, (posted_data, response_data) in enumerate(zip(requisition_data_list, response_data_list, strict=True)):
        # Check that posted fields match response fields
        assert response_data["item_id"] == posted_data["item_id"], f"Item {i}: item_id mismatch"
        assert response_data["quantity"] == posted_data["quantity"], f"Item {i}: quantity mismatch"
        assert response_data["unit"] == posted_data["unit"], f"Item {i}: unit mismatch"
        assert response_data["remark"] == posted_data["remark"], f"Item {i}: remark mismatch"
        
        # Check that response includes additional fields (like ID, timestamps, etc.)
        assert "id" in response_data
        assert "status" in response_data
        assert "created_at" in response_data
        assert "created_by" in response_data
        assert "approved_at" in response_data
        assert "approved_by" in response_data
        assert "delivered_at" in response_data
        assert "delivered_by" in response_data

def test_requisition_create_wrong_permission(client, auth_headers, requisition_data):
    """Test creating requisition with wrong permission."""
    headers = auth_headers(UserAction.MANAGE_TICKET)
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    assert response.status_code == 403

def test_requisition_create_no_auth(client, requisition_data):
    response = client.post("/requisitions/", json=[requisition_data])
    assert response.status_code == 401

def test_requisition_create_empty_list(client, auth_headers):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    requisition_data = [{}]
    response = client.post("/requisitions/", json=requisition_data, headers=headers)
    assert response.status_code == 422

def test_requisition_create_missing_fields(client, auth_headers, requisition_data):
    """Test creating requisition with missing required fields."""
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    requisition_data["item_id"] = None  # Missing item_id
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Check that required fields are mentioned in error
    error_fields = [err["loc"][-1] for err in data["detail"]]
    assert "item_id" in error_fields

def test_requisition_create_invalid_data_types(client, auth_headers, requisition_data):
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    requisition_data["item_id"] = "invalid_id"  # Should be integer
    requisition_data["quantity"] = "five"       # Should be integer
    requisition_data["unit"] = 1                 # Should be integer
    requisition_data["remark"] = 123             # Should be string
    
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_requisition_create_negative_quantity(client, auth_headers, created_item_type, created_item_brand, created_item, requisition_data):
    """Test creating requisition with negative quantity."""
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    item_id = created_item(headers, type_id, brand_id, "Model XXZ")
    requisition_data["item_id"] = item_id
    requisition_data["quantity"] = -5  # Negative quantity
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    # Response depends on model validation - could be 422 or 400
    assert response.status_code == 422

def test_requisition_create_zero_quantity(client, auth_headers, created_item_type, created_item_brand, created_item, requisition_data):
    """Test creating requisition with zero quantity."""
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    item_id = created_item(headers, type_id, brand_id, "Model XXZ")
    requisition_data["item_id"] = item_id
    requisition_data["quantity"] = 0  # Zero quantity
    response = client.post("/requisitions/", json=requisition_data, headers=headers)
    # Response depends on business logic - could be successful or error
    assert response.status_code == 422

def test_requisition_create_nonexistent_item(client, auth_headers, requisition_data):
    """Test creating requisition with non-existent item ID."""
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    requisition_data["item_id"] = 9999  # Non-existent item ID
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    assert response.status_code == 400
    data = response.json()
    assert "item with id 9999 not found" in data["detail"].lower()

def test_requisition_create_database_error(client, auth_headers, created_item_type, created_item_brand, created_item, requisition_data, monkeypatch):
    """Test handling of unexpected database errors during requisition creation."""
    headers = auth_headers(UserAction.SUBMIT_REQUISITION)
    type_id = created_item_type(headers, "Switch")
    brand_id = created_item_brand(headers, "Cisco")
    item_id = created_item(headers, type_id, brand_id, "Model XXZ")
    requisition_data["item_id"] = item_id
    
    # Mock the database function to raise an unexpected error
    def mock_create_requisition_error(*args, **kwargs):
        raise Exception("Unexpected database error")

    monkeypatch.setattr("src.routers.requisitions.create_requisition_in_db", mock_create_requisition_error)
    
    response = client.post("/requisitions/", json=[requisition_data], headers=headers)
    assert response.status_code == 500
    data = response.json()
    assert "An unexpected error occurred" in data["detail"]

