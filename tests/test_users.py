def test_create_user(client, user_data, auth_headers):
    response = client.post("/users", json=user_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]
    # Now role is validated as an integer id
    assert data["role_id"] == user_data["role_id"]
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
    # Validate the role (as integer)
    assert user["role_id"] == user_data["role_id"]
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
    # Update the user (role remains unchanged)
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
    assert data["username"] == username  # username remains unchanged
    # Role should be unchanged from the originally set value
    assert data["role_id"] == user_data["role_id"]
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

    # Create second user with a different username and email
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
def test_create_role_success(client, auth_headers):
    role_data = {
        "name": "test_role",
        "description": "A test role for testing"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == role_data["name"]
    assert data["description"] == role_data["description"]
    assert "id" in data

def test_create_duplicate_role(client, auth_headers):
    role_data = {
        "name": "duplicate_role",
        "description": "This role should only be created once"
    }
    # Create the role the first time
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200

    # Attempt to create the same role again
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_create_role_missing_name(client, auth_headers):
    role_data = {
        "description": "Role without a name"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 422
    data = response.json()
    # Expect an error message about a missing "name" field
    assert isinstance(data["detail"], list)
    assert any("name" in err.get("loc", []) for err in data["detail"])

def test_create_role_empty_description(client, auth_headers):
    """Test that creating a role with empty description is allowed."""
    role_data = {
        "name": "no_description_role",
        "description": None
    }
    
    response = client.post("/users/roles/", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == role_data["name"]
    assert data["description"] is None

def test_create_role_without_description_field(client, auth_headers):
    """Test that creating a role without including the description field succeeds."""
    role_data = {
        "name": "minimal_role"
        # description field is completely omitted
    }
    
    response = client.post("/users/roles/", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == role_data["name"]
    # Check that the API assigns a default value (likely null/None) when field is omitted
    assert "description" in data

def test_get_all_roles(client, auth_headers):
    # Create multiple roles
    roles = [
        {"name": "role1", "description": "First role"},
        {"name": "role2", "description": "Second role"}
    ]
    for role in roles:
        response = client.post("/users/roles", json=role, headers=auth_headers)
        assert response.status_code == 200

    response = client.get("/users/roles/all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Expect at least the two roles we created
    assert len(data) >= 2

def test_get_role_by_id(client, auth_headers):
    # Create a role first
    role_data = {
        "name": "role_get",
        "description": "Role to fetch by id"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    role = response.json()
    role_id = role["id"]

    # Retrieve the role by id
    response = client.get(f"/users/roles/{role_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == role_data["name"]

def test_update_role(client, auth_headers):
    # Create a role to update
    role_data = {
        "name": "role_update",
        "description": "Old description"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    role = response.json()
    role_id = role["id"]

    # Update the role's description
    update_data = {
        "name": "role_update",  # name remains the same
        "description": "New description"
    }
    response = client.patch(f"/users/roles/{role_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "New description"

def test_update_nonexistent_role(client, auth_headers):
    update_data = {
        "name": "nonexistent_role",
        "description": "This role does not exist"
    }
    # Using an id that is unlikely to exist
    response = client.patch("/users/roles/9999", json=update_data, headers=auth_headers)
    # The endpoint raises an error when role is not found
    assert response.status_code in (400, 404)
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_delete_role(client, auth_headers):
    # Create a role to delete
    role_data = {
        "name": "role_delete",
        "description": "Role to be deleted"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    role = response.json()
    role_id = role["id"]

    # Delete the role
    response = client.delete(f"/users/roles/{role_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert f"Role with ID {role_id} deleted successfully" in data["message"]

    # Verify deletion by attempting to retrieve the deleted role
    response = client.get(f"/users/roles/{role_id}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_nonexistent_role(client, auth_headers):
    response = client.delete("/users/roles/9999", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Role not found"

def test_delete_role_with_referenced_role_permission(client, auth_headers):
    # Create a new role
    role_data = {
        "name": "role_referenced",
        "description": "Role referenced by role permission"
    }
    response = client.post("/users/roles", json=role_data, headers=auth_headers)
    assert response.status_code == 200
    role = response.json()
    role_id = role["id"]

    # Create a role permission referencing this role
    role_permission_data = {
        "role_id": role_id,
        "permission": "manage_ticket"
    }
    response_rp = client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)
    assert response_rp.status_code == 200

    # Attempt to delete the role; should fail due to integrity constraints
    response_del = client.delete(f"/users/roles/{role_id}", headers=auth_headers)
    assert response_del.status_code == 400
    data = response_del.json()
    assert "Role cannot be deleted" in data["detail"]

def test_create_role_permission(client, role_id, auth_headers):
    role_permission_data = {
        "role_id": role_id,
        "permission": "manage_ticket"
    }
    response = client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == role_permission_data["role_id"]
    assert data["permission"] == role_permission_data["permission"]

def test_create_duplicate_role_permission(client, role_id, auth_headers):
    role_permission_data = {
        "role_id": role_id,
        "permission": "update_ticket"
    }
    # Create the role permission the first time
    response = client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)
    assert response.status_code == 200
    # Attempt to create the same permission again
    response_dup = client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)
    assert response_dup.status_code == 400
    data = response_dup.json()
    assert "already exists" in data["detail"]

def test_delete_role_permission(client, role_id, auth_headers):
    role_permission_data = {
        "role_id": role_id,
        "permission": "manage_ticket"
    }
    # First, create the permission so it can be deleted
    response = client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)
    assert response.status_code == 200

    # Delete the permission
    response_del = client.delete("/users/roles/permissions/", params=role_permission_data, headers=auth_headers)
    assert response_del.status_code == 200
    data = response_del.json()
    expected_message = f"Role permission {role_permission_data['permission']} for Role ID {role_permission_data['role_id']} successfully deleted"
    assert expected_message in data["message"]

def test_delete_nonexistent_role_permission(client, role_id, auth_headers):
    # Attempt to delete a role permission that does not exist
    role_permission_data = {
        "role_id": role_id,
        "permission": "manage_ticket"
    }
    response = client.delete("/users/roles/permissions/", params=role_permission_data, headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_get_all_role_permissions(client, role_id, auth_headers):
    # Create two role permissions for the same role
    perm1 = {"role_id": role_id, "permission": "manage_ticket"}
    perm2 = {"role_id": role_id, "permission": "update_ticket"}
    # Ensure the permissions exist (ignore duplicate errors)
    client.post("/users/roles/permissions/", json=perm1, headers=auth_headers)
    client.post("/users/roles/permissions/", json=perm2, headers=auth_headers)

    response = client.get("/users/roles/permissions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Check that the created permissions are among the returned list
    permissions_list = [item["permission"] for item in data if item["role_id"] == role_id]
    assert "manage_ticket" in permissions_list
    assert "update_ticket" in permissions_list

def test_get_role_permissions_by_role_name(client, role_id, auth_headers):
    # First, get the role name using the role id
    response_role = client.get(f"/users/roles/{role_id}", headers=auth_headers)
    assert response_role.status_code == 200
    role_data = response_role.json()
    role_name = role_data["name"]

    # Create a permission for this role if not already present
    role_permission_data = {"role_id": role_id, "permission": "manage_ticket"}
    client.post("/users/roles/permissions/", json=role_permission_data, headers=auth_headers)

    # Retrieve permissions by role name
    response = client.get(f"/users/roles/permissions/by-name/{role_name}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # Verify that each returned permission belongs to the role we queried
    for item in data:
        assert item["role_id"] == role_id
