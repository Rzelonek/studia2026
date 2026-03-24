import os
import sys
import csv
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app import create_app
from models import db, User, Task

OUTPUT_DIR = "/seed_output"


def seed_data():
    app = create_app()

    with app.app_context():
        if User.query.count() == 0:
            users = [
                User(name="Jan Kowalski", email="jan@example.com"),
                User(name="Anna Nowak", email="anna@example.com"),
                User(name="Piotr Zielinski", email="piotr@example.com"),
                User(name="Maria Wisla", email="maria@example.com"),
                User(name="Tomasz Kaczmarek", email="tomasz@example.com"),
            ]
            db.session.add_all(users)
            db.session.commit()

        if Task.query.count() == 0:
            users = User.query.order_by(User.id.asc()).all()

            tasks = [
                Task(title="Prepare project documentation", description="Write README and architecture notes", status="todo", user_id=users[0].id),
                Task(title="Configure Nginx", description="Verify reverse proxy configuration", status="in_progress", user_id=users[1].id),
                Task(title="Write tests", description="Add pytest coverage for API", status="done", user_id=users[2].id),
                Task(title="Prepare CI pipeline", description="Create GitHub Actions workflows", status="todo", user_id=users[3].id),
                Task(title="Validate Docker Compose", description="Check networks and volumes", status="done", user_id=users[4].id),
                Task(title="Prepare Azure IaC", description="Add Bicep templates", status="in_progress", user_id=users[0].id),
            ]
            db.session.add_all(tasks)
            db.session.commit()

        users = User.query.order_by(User.id.asc()).all()
        tasks = Task.query.order_by(Task.id.asc()).all()

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with open(os.path.join(OUTPUT_DIR, "seed.log"), "w", encoding="utf-8") as f:
            f.write(f"Seed executed at {datetime.now()}\n")
            f.write(f"Users in database: {len(users)}\n")
            f.write(f"Tasks in database: {len(tasks)}\n")

        with open(os.path.join(OUTPUT_DIR, "users.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "email"])
            for user in users:
                writer.writerow([user.id, user.name, user.email])

        with open(os.path.join(OUTPUT_DIR, "tasks.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "description", "status", "user_id", "user_name"])
            for task in tasks:
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.status,
                    task.user_id,
                    task.user.name if task.user else ""
                ])

        with open(os.path.join(OUTPUT_DIR, "data.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "users": [user.to_dict(include_tasks=True) for user in users],
                    "tasks": [task.to_dict() for task in tasks]
                },
                f,
                ensure_ascii=False,
                indent=2
            )

        print("Seed completed successfully.")


if __name__ == "__main__":
    seed_data()