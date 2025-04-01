import flask as f
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
# import os
from models import User, Admin, GameResult, db
from datetime import datetime, timezone #do testowego uzytkownika

#name app routes accordingly, not random bs

app = f.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "your_secret_key"
db.init_app(app)

@app.route('/')
def home():
    return f.render_template('index.html')

@app.route('/my_profile')
def user():
    return f.render_template('user.html')

@app.route('/edit')
def edit_user():
    return f.render_template('edit_user.html')

@app.route('/login')
def login():
    return f.render_template('login.html')

@app.route('/register')
def register():
    return f.render_template('register.html')

@app.route('/user_panel', methods=['POST'])
def myprof_from_index():
    if f.session["email"] and f.session["password"]:
        return f.render_template('user.html')
    else:
        #has to be handled better
        return "You are not logged in"

@app.route('/handle_login', methods=['POST'])
def handle_login():
    email_input_login = f.request.form.get('email_input_login')
    password_input_login = f.request.form.get('password_input_login')

    print(email_input_login, password_input_login)

    user_exists = User.query.filter_by(email=email_input_login, password=password_input_login).first()
    if not user_exists:
        #has to be handled better
        return "User doesn't exist in database"
    else:
        f.session["email"] = email_input_login
        f.session["password"] = password_input_login
        #maybe is handled alright
        return f.render_template('user.html')


@app.route('/handle_register', methods=['POST'])
def handle_register():
    email_input_reg = f.request.form.get('email_input_reg')
    username_input_reg = f.request.form.get('username_input_reg')
    password_input_reg = f.request.form.get('password_input_reg')
    confirm_password_input_reg = f.request.form.get('confirm_password_input_reg')
    terms_conditions_input_reg = f.request.form.get('terms_conditions_input_reg')
    print("terms: ", terms_conditions_input_reg)
    print(email_input_reg, username_input_reg, password_input_reg, confirm_password_input_reg)

    if not terms_conditions_input_reg:
        #has to be handled better
        return "You have to accept the terms and conditions"

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

@app.route('/edit', methods=['POST'])
def edit():
    # get all the data
    username_edit = f.request.form.get('username_edit')
    email_edit = f.request.form.get('email_edit')
    oldpassword_edit = f.request.form.get('oldpassword_edit')
    newpassword_edit = f.request.form.get('newpassword_edit')
    confirmpassword_edit = f.request.form.get('confirmpassword_edit')

    print(username_edit, email_edit, oldpassword_edit, newpassword_edit, confirmpassword_edit)


    # username_exists = db.session.query(User).filter_by(username=username_edit).first()

    session_email = f.session["email"]

    return f.render_template('edit_user.html')

@app.route('/handle_logout', methods=['POST'])
#needs work but works
def handle_logout():
    f.session["email"]
    f.session["password"]
    f.session.clear()
    print("I'm written in python!!!!!!!!!!!!!!!!")
    return f.render_template('login.html')

@app.route('/debug')
def show_tables():
    users = User.query.all()
    result = "<h2>Lista użytkowników</h2><ul>"
    for user in users:
        result += f"<li>ID: {user.user_id}, Username: {user.username}, Email: {user.email}</li>"
    result += "</ul>"
    return result

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = f.session.get("user_id")
    if not user_id:
        return "Nie jesteś zalogowany"

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        f.session.clear()
        return f.redirect(f.url_for('home'))  
    return "Użytkownik nie istnieje"

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
        #testowy uzytkownik
        existing_user = User.query.filter_by(username='testuser').first()
        if not existing_user:
            test_user = User(
                username='testuser',
                password='test123', 
                email='test@gmail.com',
                registration_date=datetime.now(timezone.utc)
            )
            db.session.add(test_user)
            db.session.commit()
            print("Testowy użytkownik został dodany.")
        else:
            print("Testowy użytkownik już istnieje.")

    app.run(debug=True)
