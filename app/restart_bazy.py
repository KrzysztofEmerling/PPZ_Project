from flask import Flask
from models import db, User, Admin, GameResult
import os
app = Flask(__name__, instance_relative_config=False)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    print("DROP WSZYSTKICH TABEL")
    db.drop_all()

    print("CREATE NOWYCH TABEL")
    db.create_all()

    print("Gotowe – struktura zaktualizowana!")


    print("Absolutna ścieżka do pliku DB:", os.path.abspath("database.db"))    
