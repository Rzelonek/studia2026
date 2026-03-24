from flask import Flask, jsonify, request, render_template
from flask_migrate import Migrate

from config import Config
from models import db, User, Task

ALLOWED_TASK_STATUSES = {"todo", "in_progress", "done"}

migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "ok", "code": 200}), 200

    @app.route("/api/stats")
    def api_stats():
        total_users = User.query.count()
        total_tasks = Task.query.count()
        todo_tasks = Task.query.filter_by(status="todo").count()
        in_progress_tasks = Task.query.filter_by(status="in_progress").count()
        done_tasks = Task.query.filter_by(status="done").count()

        return jsonify({
            "total_users": total_users,
            "total_tasks": total_tasks,
            "todo_tasks": todo_tasks,
            "in_progress_tasks": in_progress_tasks,
            "done_tasks": done_tasks
        }), 200

    @app.route("/users")
    def get_users_legacy():
        users = User.query.order_by(User.id.asc()).all()
        return jsonify([user.to_dict() for user in users]), 200

    @app.route("/users/<int:user_id>")
    def get_user_legacy(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict(include_tasks=True)), 200

    @app.route("/api/users", methods=["GET"])
    def api_get_users():
        users = User.query.order_by(User.id.asc()).all()
        return jsonify([user.to_dict(include_tasks=True) for user in users]), 200

    @app.route("/api/users/<int:user_id>", methods=["GET"])
    def api_get_user(user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict(include_tasks=True)), 200

    @app.route("/api/users", methods=["POST"])
    def api_create_user():
        data = request.get_json() or {}

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()

        if not name or not email:
            return jsonify({"error": "Name and email are required"}), 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"error": "User with this email already exists"}), 409

        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 201

    @app.route("/api/users/<int:user_id>", methods=["PUT"])
    def api_update_user(user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json() or {}

        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()

        if not name or not email:
            return jsonify({"error": "Name and email are required"}), 400

        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            return jsonify({"error": "Another user with this email already exists"}), 409

        user.name = name
        user.email = email
        db.session.commit()

        return jsonify(user.to_dict()), 200

    @app.route("/api/users/<int:user_id>", methods=["DELETE"])
    def api_delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted"}), 200

    @app.route("/api/users/<int:user_id>/tasks", methods=["GET"])
    def api_get_user_tasks(user_id):
        user = User.query.get_or_404(user_id)
        tasks = Task.query.filter_by(user_id=user.id).order_by(Task.id.asc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200

    @app.route("/api/tasks", methods=["GET"])
    def api_get_tasks():
        tasks = Task.query.order_by(Task.id.asc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200

    @app.route("/api/tasks/<int:task_id>", methods=["GET"])
    def api_get_task(task_id):
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks", methods=["POST"])
    def api_create_task():
        data = request.get_json() or {}

        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()
        status = (data.get("status") or "todo").strip()
        user_id = data.get("user_id")

        if not title:
            return jsonify({"error": "Title is required"}), 400

        if status not in ALLOWED_TASK_STATUSES:
            return jsonify({"error": "Invalid task status"}), 400

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "Assigned user not found"}), 404

        task = Task(
            title=title,
            description=description,
            status=status,
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()

        return jsonify(task.to_dict()), 201

    @app.route("/api/tasks/<int:task_id>", methods=["PUT"])
    def api_update_task(task_id):
        task = Task.query.get_or_404(task_id)
        data = request.get_json() or {}

        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()
        status = (data.get("status") or "").strip()
        user_id = data.get("user_id")

        if not title:
            return jsonify({"error": "Title is required"}), 400

        if status not in ALLOWED_TASK_STATUSES:
            return jsonify({"error": "Invalid task status"}), 400

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "Assigned user not found"}), 404

        task.title = title
        task.description = description
        task.status = status
        task.user_id = user_id
        db.session.commit()

        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def api_delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()

        return jsonify({"message": "Task deleted"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)