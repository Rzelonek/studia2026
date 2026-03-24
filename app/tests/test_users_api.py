def test_get_users(client):
    response = client.get("/api/users")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == "Anna Nowak"


def test_get_single_user(client):
    response = client.get("/api/users/1")
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Anna Nowak"
    assert "tasks" in data


def test_get_user_tasks(client):
    response = client.get("/api/users/1/tasks")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == "Prepare CI pipeline"


def test_create_user(client):
    payload = {
        "name": "Maria Wisla",
        "email": "maria@example.com"
    }

    response = client.post("/api/users", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["name"] == "Maria Wisla"
    assert data["email"] == "maria@example.com"


def test_create_user_validation_error(client):
    payload = {
        "name": "",
        "email": ""
    }

    response = client.post("/api/users", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_create_user_duplicate_email(client):
    payload = {
        "name": "Other Anna",
        "email": "anna@example.com"
    }

    response = client.post("/api/users", json=payload)
    data = response.get_json()

    assert response.status_code == 409
    assert "error" in data


def test_update_user(client):
    payload = {
        "name": "Anna Updated",
        "email": "anna.updated@example.com"
    }

    response = client.put("/api/users/1", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["name"] == "Anna Updated"
    assert data["email"] == "anna.updated@example.com"


def test_delete_user(client):
    response = client.delete("/api/users/2")
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "User deleted"

    follow_up = client.get("/api/users")
    follow_up_data = follow_up.get_json()
    assert len(follow_up_data) == 1