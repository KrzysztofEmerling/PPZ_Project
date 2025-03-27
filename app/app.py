# from flask import Flask
import flask as f
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
# from sqlalchemy import inspect
import os

# Inicjalizacja aplikacji Flask
app = f.Flask(__name__)

# Konfiguracja bazy danych (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "database.db")  # Ścieżka do bazy danych
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicjalizacja SQLAlchemy
db = SQLAlchemy(app)

@app.route('/')
def home():
    return f.render_template('index.html')

@app.route('/login')
def login():
    return f.render_template('login.html')

@app.route('/register')
def register():
    return f.render_template('register.html')

@app.route('/handle_login', methods=['POST'])
def handle_login():
    user_name = f.request.form.get('floatingInput')  # Pobranie nazwy użytkownika
    password = f.request.form.get('floatingPassword')  # Pobranie hasła

    
    # Sprawdzenie, czy użytkownik istnieje w bazie danych
    user = db.session.execute(text("SELECT email FROM users WHERE email = :email"), {"email": user_name}).fetchone()


    if user:
        return f"Przesłane dane:<br>Użytkownik: {user_name}<br>Hasło: {password}"
    else:
        return "Nie ma takiego użytkownika"

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/debug')
def show_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    table_info = {}
    for table in tables:
        columns = [column["name"] for column in inspector.get_columns(table)]
        table_info[table] = columns

    # Pobieranie danych dla każdej tabeli
    result = ""
    for table, columns in table_info.items():
        result += f"<b>Tabela:</b> {table} <br><b>Kolumny:</b> {', '.join(columns)}<br>"
        
        # Pobieranie pierwszych 5 rekordów z tabeli
        query = text(f"SELECT * FROM {table}")
        rows = db.session.execute(query).fetchall()
        
        if rows:
            result += "<b>Dane:</b><br>"
            for row in rows:
                result += f"{row}<br>"
        else:
            result += "Brak danych.<br>"

        result += "<hr>"

    return result



if __name__ == '__main__':
    app.run(debug=True)