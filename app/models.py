from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(100), unique = True)
    registration_date = db.Column(db.Date, default=datetime.now(timezone.utc))

class Admin(db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    user = db.relationship("User", backref=db.backref("admin", uselist=False, cascade="all, delete"))

class GameResult(db.Model):
    __tablename__ = "game_results"
    result_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"))
    completion_time = db.Column(db.Integer, nullable = False)
    difficulty = db.Column(db.String(10), nullable = False)
    user = db.relationship("User", backref=db.backref("games", lazy=True))


def init_db(app):
    with app.app_context():
       db.create_all()
       print("Baza danych jest utworzona")
