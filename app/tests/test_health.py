import os
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import create_app
from models import db, User, Task


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()

        user1 = User(name="Anna Nowak", email="anna@example.com")
        user2 = User(name="Jan Kowalski", email="jan@example.com")
        db.session.add_all([user1, user2])
        db.session.commit()

        task1 = Task(
            title="Prepare CI pipeline",
            description="Create GitHub Actions workflows",
            status="todo",
            user_id=user1.id
        )
        task2 = Task(
            title="Write API tests",
            description="Add endpoint coverage",
            status="done",
            user_id=user2.id
        )
        db.session.add_all([task1, task2])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()