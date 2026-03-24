def test_api_stats_endpoint(client):
    response = client.get("/api/stats")
    data = response.get_json()

    assert response.status_code == 200
    assert data["total_users"] == 2
    assert data["total_tasks"] == 2
    assert data["todo_tasks"] == 1
    assert data["in_progress_tasks"] == 0
    assert data["done_tasks"] == 1