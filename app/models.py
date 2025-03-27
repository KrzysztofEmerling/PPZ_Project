from sqlalchemy import SQLAlchemy

# Inicjalizacja bazy danych
db = SQLAlchemy()

def init_db(app):
    # Tworzenie tabel w bazie danych
    with app.app_context():
        db.create_all()

# Definicja modelu
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"



# app = f.Flask(__name__)


# BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
# DB_PATH = os.path.join(BASE_DIR, "../database.db") 
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db.init_app(app)
# init_db(app)