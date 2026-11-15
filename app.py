
from flask import Flask, jsonify, request
from datetime import date, datetime, timezone
from sqlalchemy.exc import IntegrityError

from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


# GET: Retrieve student by ID
@app.route("/info/<student_id>", methods=["GET"])
def get_user(student_id):
    user = db.session.get(User, student_id)

    if user is None:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        **user.to_dict(),
        "timestamp": timestamp()
    }), 200


# POST: Create a new student
@app.route("/info", methods=["POST"])
def add_user():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body"}), 400

    required_fields = [
        "student_id", "name", "birthday", "email", "age"
    ]

    if any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    student_id = str(data["student_id"])

    if db.session.get(User, student_id) is not None:
        return jsonify({"error": "Student ID already exists"}), 409

    try:
        birthday = date.fromisoformat(data["birthday"])
        age = int(data["age"])

        if isinstance(data["age"], bool) or age < 0:
            raise ValueError

    except (ValueError, TypeError, KeyError):
        return jsonify({
            "error": "Invalid birthday or age"
        }), 400

    user = User(
        student_id=student_id,
        name=data["name"],
        birthday=birthday,
        email=data["email"],
        age=age
    )

    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Student ID or email already exists"
        }), 409

    return jsonify({
        "message": "User created successfully",
        **user.to_dict(),
        "timestamp": timestamp()
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
