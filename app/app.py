import flask as f
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
# import os
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
    email_input_login = f.request.form.get('email_input_login')
    password_input_login = f.request.form.get('password_input_login')

    print(email_input_login, password_input_login)

    user_exists = User.query.filter_by(email=email_input_login, password=password_input_login).first()
    if user_exists:
        #has to be handled better
        return "User exists in database"
    else:
        #has to be handled better
        return "User doesn't exist in database"


    # user = db.session.query(User).filter_by(email=email_input_login).first()
    # print(type(user))


    # if user:
    #     return f"Przesłane dane:<br>Użytkownik: {email_input_login}<br>Hasło: {password_input_login}"
    # else:
    #     return "Nie ma takiego użytkownika"
    
@app.route('/handle_register', methods=['POST'])
def handle_register():

    email_input_reg = f.request.form.get('email_input_reg')
    username_input_reg = f.request.form.get('username_input_reg')
    password_input_reg = f.request.form.get('password_input_reg')
    confirm_password_input_reg = f.request.form.get('confirm_password_input_reg')
    print(email_input_reg, username_input_reg, password_input_reg, confirm_password_input_reg)


    if password_input_reg != confirm_password_input_reg:
        #has to be handled better
        return "Passwords don't match"
    
    email_exists = db.session.query(User).filter_by(email=email_input_reg).first()
    if email_exists:
        #has to be handled better
        return "Email already exists"
    
    username_exists = db.session.query(User).filter_by(username=username_input_reg).first()
    if username_exists:
        #has to be handled better
        return "Username already exists"
    
    #if user can be added
    user = User(email=email_input_reg, username=username_input_reg, password=password_input_reg)
    db.session.add(user)
    db.session.commit()
    
    return f.render_template('login.html')

    # return "Stuff" #stuff shown on site handle_register. Should it put user to login page?

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
