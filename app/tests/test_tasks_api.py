def test_get_tasks(client):
    response = client.get("/api/tasks")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "Prepare CI pipeline"


def test_get_single_task(client):
    response = client.get("/api/tasks/1")
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "Prepare CI pipeline"


def test_create_task(client):
    payload = {
        "title": "Prepare Azure IaC",
        "description": "Add Bicep template",
        "status": "in_progress",
        "user_id": 1
    }

    response = client.post("/api/tasks", json=payload)
    data = response.get_json()

    assert response.status_code == 201
    assert data["title"] == "Prepare Azure IaC"
    assert data["status"] == "in_progress"
    assert data["user_id"] == 1


def test_create_task_invalid_status(client):
    payload = {
        "title": "Bad status task",
        "description": "Wrong status",
        "status": "invalid_status",
        "user_id": 1
    }

    response = client.post("/api/tasks", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_create_task_missing_title(client):
    payload = {
        "title": "",
        "description": "No title",
        "status": "todo",
        "user_id": 1
    }

    response = client.post("/api/tasks", json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "error" in data


def test_update_task(client):
    payload = {
        "title": "Write API tests updated",
        "description": "Expanded endpoint coverage",
        "status": "in_progress",
        "user_id": 2
    }

    response = client.put("/api/tasks/2", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["title"] == "Write API tests updated"
    assert data["status"] == "in_progress"


def test_delete_task(client):
    response = client.delete("/api/tasks/1")
    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Task deleted"

    follow_up = client.get("/api/tasks")
    follow_up_data = follow_up.get_json()
    assert len(follow_up_data) == 1