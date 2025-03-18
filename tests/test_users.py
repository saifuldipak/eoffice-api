def test_create_user(client, user_data, auth_headers):
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_duplicate_user(client, user_data, auth_headers):
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Attempt to create the same user again
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User with this username or email already exists"

def test_create_user_missing_username(client, user_data, auth_headers):
    user_data.pop("username")
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["loc"][-1] == "username"

def test_create_user_missing_email(client, user_data, auth_headers):
    user_data.pop("email")
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["loc"][-1] == "email"

def test_get_user_by_username(client, user_data, auth_headers):
    # Create a user first
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Get the user by username
    username = user_data["username"]
    response = client.get(f"/users/{username}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    user = data[0]
    assert user["username"] == user_data["username"]
    assert user["first_name"] == user_data["first_name"]
    assert user["last_name"] == user_data["last_name"]
    assert user["email"] == user_data["email"]
    assert user["role"] == user_data["role"]
    assert "id" in user
    assert "created_at" in user
    assert "updated_at" in user

def test_get_nonexistent_user(client, auth_headers):
    # Attempt to get a user that does not exist
    response = client.get("/users/nonexistentuser", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No users found"

def test_delete_user(client, user_data, auth_headers):
    # Create a user first
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Delete the user
    username = user_data["username"]
    response = client.delete(f"/users/{username}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"User {username} successfully deleted"

    # Verify user no longer exists
    response = client.get(f"/users/{username}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_nonexistent_user(client, auth_headers):
    # Attempt to delete a user that does not exist
    response = client.delete("/users/nonexistentuser", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

def test_update_user(client, user_data, auth_headers):
    # Create a user first
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Update the user
    username = user_data["username"]
    update_data = {
        "first_name": "Updated First",
        "last_name": "Updated Last",
        "email": "updated@example.com"
    }
    response = client.patch(f"/users/{username}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["email"] == update_data["email"]
    assert data["username"] == username  # username should not change
    assert "updated_at" in data

def test_update_nonexistent_user(client, auth_headers):
    update_data = {"first_name": "New Name"}
    response = client.patch("/users/nonexistentuser", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_update_user_no_data(client, user_data, auth_headers):
    # Create a user first
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Attempt to update with empty data
    username = user_data["username"]
    response = client.patch(f"/users/{username}", json={}, headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "No valid fields to update"

def test_update_user_duplicate_email(client, user_data, auth_headers):
    # Create first user
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200

    # Create second user
    second_user = user_data.copy()
    second_user["username"] = "seconduser"
    second_user["email"] = "second@example.com"
    response = client.post("/users", json=second_user, headers=auth_headers)
    assert response.status_code == 200

    # Try to update second user with first user's email
    update_data = {"email": user_data["email"]}
    response = client.patch(f"/users/{second_user['username']}", 
                          json=update_data, 
                          headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists"