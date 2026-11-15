# DB_URL: $env:DATABASE_URL = "postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/user_db"
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    student_id = db.Column(
        db.String(20), primary_key=True
    )

    name = db.Column(
        db.String(100), nullable=False
    )

    birthday = db.Column(
        db.Date, nullable=False
    )

    email = db.Column(
        db.String(120), unique=True, nullable=False
    )

    age = db.Column(
        db.Integer, nullable=False
    )

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "birthday": self.birthday.isoformat(),
            "email": self.email,
            "age": self.age
        }
