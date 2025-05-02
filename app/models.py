from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    """
    Model użytkownika.

    Attributes:
        user_id (int): Unikalny identyfikator użytkownika (klucz główny).
        username (str): Nazwa użytkownika (unikalna, wymagana).
        password (str): Zahasłowane, solone hasło użytkownika (wymagane).
        email (str): Adres e-mail użytkownika (unikalny).
        registration_date (date): Data rejestracji użytkownika (domyślnie bieżąca data).
    """
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(100), unique = True)
    registration_date = db.Column(db.Date, default=datetime.now(timezone.utc))

class Admin(db.Model):
    """
    Model administratora — rozszerzenie modelu User.

    Attributes:
        admin_id (int): Unikalny identyfikator administratora (klucz główny).
        user_id (int): Odwołanie do tabeli users (unikalne i wymagane).
        user (User): Obiekt użytkownika powiązany z tym administratorem.
    """
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    user = db.relationship("User", backref=db.backref("admin", uselist=False, cascade="all, delete"))

class GameResult(db.Model):
    """
    Model wyników gry.

    Attributes:
        result_id (int): Unikalny identyfikator wyniku (klucz główny).
        user_id (int): Odwołanie do użytkownika, który osiągnął wynik.
        difficulty (str): Poziom trudności gry.
        date_played (date): Data rozegrania gry (domyślnie bieżąca data).
        time_finished (int): Czas ukończenia gry (w sekundach).
        user (User): Obiekt użytkownika, do którego przypisany jest wynik.
    """
    __tablename__ = "game_results"
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE")) 
    difficulty = db.Column(db.String(10), nullable=False)
    date_played = db.Column(db.Date, default=datetime.utcnow().date) 
    time_finished = db.Column(db.Integer, nullable=False) 
    user = db.relationship("User", backref=db.backref("games", lazy=True))

def init_db(app):
    """
    Inicjalizuje bazę danych w kontekście aplikacji Flask.

    Tworzy wszystkie tabele zdefiniowane w modelach, jeśli jeszcze nie istnieją.
    
    Args:
        app (Flask): Obiekt aplikacji Flask.
    """
    with app.app_context():
       db.create_all()
       print("Baza danych jest utworzona")
