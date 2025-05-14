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

    # Create a team to update user's team_id to
    team_data = {
        "name": "TeamForUpdate",
        "description": "Team for updating user's team_id"
    }
    team_resp = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert team_resp.status_code == 200
    team = team_resp.json()

    # Update the user including team_id update
    username = user_data["username"]
    update_data = {
        "first_name": "Updated First",
        "last_name": "Updated Last",
        "email": "updated@example.com",
        "team_id": team["id"]
    }
    response = client.patch(f"/users/{username}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["email"] == update_data["email"]
    assert data["username"] == username  # username should not change
    assert data["team_id"] == team["id"]
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
    assert response.json()["detail"] == "Update failed due to integrity constraints (e.g., duplicate username or email)"

def test_create_user_with_team_id(client, user_data, auth_headers):
    # Create a team first
    team_data = {
        "name": "TestTeam",
        "description": "Team for testing user creation with team_id"
    }
    team_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert team_response.status_code == 200
    created_team = team_response.json()
    team_id = created_team["id"]

    # Set team_id in user data and create the user
    user_data["team_id"] = team_id
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["team_id"] == team_id

def test_create_team(client, auth_headers):
    team_data = {
        "name": "TeamAlpha",
        "description": "Alpha team description"
    }
    response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]
    assert "id" in data

def test_create_duplicate_team(client, auth_headers):
    team_data = {
        "name": "TeamBeta",
        "description": "Beta team description"
    }
    # First creation should succeed.
    response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert response.status_code == 200

    # Duplicate creation should fail.
    response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Team with this name or description already exists"

def test_get_team(client, auth_headers):
    team_data = {
        "name": "TeamGamma",
        "description": "Gamma team description"
    }
    # Create the team first.
    create_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert create_response.status_code == 200

    # Get the team by name.
    response = client.get(f'/users/teams/{team_data["name"]}', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]
    assert "id" in data

def test_get_nonexistent_team(client, auth_headers):
    response = client.get("/users/teams/NonExistentTeam", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Team not found"

def test_list_teams(client, auth_headers):
    # Create two teams.
    teams = [
        {"name": "TeamDelta", "description": "Delta team description"},
        {"name": "TeamEpsilon", "description": "Epsilon team description"}
    ]
    for team in teams:
        response = client.post("/users/teams/", json=team, headers=auth_headers)
        assert response.status_code == 200

    # List teams.
    response = client.get("/users/teams/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Assert at least two teams are present.
    assert isinstance(data, list)
    assert len(data) >= 2

def test_update_team(client, auth_headers):
    # Create a team.
    team_data = {
        "name": "TeamZeta",
        "description": "Zeta team description"
    }
    create_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert create_response.status_code == 200

    # Update the team's description.
    update_data = {
        "name": "TeamZeta",  # Assuming name is required to identify the team in the update object.
        "description": "Updated Zeta team description"
    }
    response = client.patch(f'/users/teams/{team_data["name"]}', json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]
    # Name should remain unchanged.
    assert data["name"] == team_data["name"]

def test_update_team_same_description(client, auth_headers):
    # Create a team.
    team_data = {
        "name": "TeamZeta",
        "description": "Zeta team description"
    }
    create_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert create_response.status_code == 200

    # Attempt an update with the same description to trigger a no-change error.
    update_data = {
        "name": "TeamZeta",  # Identifies the team.
        "description": "Zeta team description"
    }
    response = client.patch(f'/users/teams/{team_data["name"]}', json=update_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "No changes detected in team description"

def test_update_nonexistent_team(client, auth_headers):
    update_data = {
        "name": "NonExistentTeam",
        "description": "Some description"
    }
    response = client.patch("/users/teams/NonExistentTeam", json=update_data, headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Team not found"

def test_delete_team(client, auth_headers):
    # Create a team to delete.
    team_data = {
        "name": "TeamTheta",
        "description": "Theta team description"
    }
    create_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert create_response.status_code == 200
    created_team = create_response.json()
    team_name = created_team["name"]

    # Delete the team.
    delete_response = client.delete(f"/users/teams/{team_name}", headers=auth_headers)
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert team_data["name"] in data["message"]

    # Verify deletion by trying to get the team.
    get_response = client.get(f'/users/teams/{team_data["name"]}', headers=auth_headers)
    assert get_response.status_code == 404
    data = get_response.json()
    assert data["detail"] == "Team not found"

def test_delete_team_referenced_in_users(client, user_data, auth_headers):
    # Create a team.
    team_data = {
        "name": "TeamReferenced",
        "description": "Team referenced in a user."
    }
    team_response = client.post("/users/teams/", json=team_data, headers=auth_headers)
    assert team_response.status_code == 200
    created_team = team_response.json()
    team_name = created_team["name"]

    # Create a user who is associated with the team.
    # Assuming the user model has a field like "team_id" to reference the team.
    user_data["team_id"] = created_team["id"]
    user_response = client.post("/users", json=user_data, headers=auth_headers)
    assert user_response.status_code == 200

    # Attempt to delete the team.
    delete_response = client.delete(f"/users/teams/{team_name}", headers=auth_headers)
    # Expecting a 400 Bad Request, adjust if your API returns a different status code.
    assert delete_response.status_code == 400
    data = delete_response.json()
    # Adjust the assertion to match the actual error message from your API.
    assert "cannot be deleted" in data["detail"].lower()