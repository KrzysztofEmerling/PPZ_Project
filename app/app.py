from flask import Flask
from models import db, init_db
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
DB_PATH = os.path.join(BASE_DIR, "../database.db") 
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
init_db(app)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)