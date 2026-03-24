from models import User, Task


def test_user_to_dict():
    user = User(id=1, name="Jan", email="jan@example.com")
    data = user.to_dict()

    assert data["id"] == 1
    assert data["name"] == "Jan"
    assert data["email"] == "jan@example.com"


def test_task_to_dict():
    task = Task(
        id=1,
        title="Prepare CI",
        description="Create GitHub Actions pipeline",
        status="todo",
        user_id=1
    )
    data = task.to_dict()

    assert data["id"] == 1
    assert data["title"] == "Prepare CI"
    assert data["description"] == "Create GitHub Actions pipeline"
    assert data["status"] == "todo"
    assert data["user_id"] == 1