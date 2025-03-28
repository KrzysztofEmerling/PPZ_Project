import flask as f
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import os
from models import User, Admin, GameResult, db

app = f.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
    user_name = f.request.form.get('floatingInput')  
    password = f.request.form.get('floatingPassword')  

    user = db.session.query(User).filter_by(email=user_name).first()


    if user:
        return f"Przesłane dane:<br>Użytkownik: {user_name}<br>Hasło: {password}"
    else:
        return "Nie ma takiego użytkownika"

@app.route('/debug')
def show_tables():
    users = User.query.all()
    result = "<h2>Lista użytkowników</h2><ul>"
    for user in users:
        result += f"<li>ID: {user.id}, Username: {user.username}, Email: {user.email}</li>"
    result += "</ul>"
    return result

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
