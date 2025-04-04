import flask as f
from models import User, db
from datetime import datetime, timezone

routes = f.Blueprint('routes', __name__)

@routes.route('/')
def home():
    return f.render_template('index.html', logged_user_data = f.session)

@routes.route('/my_profile')
def user():
    return f.render_template('user.html', logged_user_data = f.session)

@routes.route('/edit')
def edit_user():
    return f.render_template('edit_user.html')

@routes.route('/login')
def login():
    return f.render_template('login.html')

@routes.route('/register')
def register():
    return f.render_template('register.html')

# NOT YET IMPLEMENTED - printing correct data in user panel
# @app.route('/user_data')
# def user_data():
#     user = db.session.query(User).filter_by(email=f.session["email"]).first()
#     data = {
#         "email": user.email,
#         "username": user.username,
#         "registration_date": user.registration_date
#     }
#     return 

@routes.route('/user_panel', methods=['POST'])
def myprof_from_index():
    if "email" in f.session and "password" in f.session:
        return f.render_template('user.html', logged_user_data = f.session)
    
    else:
        f.flash("You are not logged in", "danger")
        return f.redirect(f.url_for('routes.login'))

@routes.route('/handle_login', methods=['POST'])
def handle_login():
    email_input_login = f.request.form.get('email_input_login')
    password_input_login = f.request.form.get('password_input_login')

    email_exists = User.query.filter_by(email=email_input_login).first()
    user_exists = User.query.filter_by(email=email_input_login, password=password_input_login).first()

    if not email_exists:
        f.flash("Email doesn't exist in database!", "danger")
        return f.render_template('login.html', logged_user_data = f.session)
    
    elif not user_exists:
        f.flash("Wrong password!", "danger")
        return f.render_template('login.html', logged_user_data = f.session)
    
    else:
        user = db.session.query(User).filter_by(email=email_input_login, password = password_input_login).first()
        f.session["email"] = email_input_login
        f.session["password"] = password_input_login
        f.session["username"] = user.username
        f.session["user_id"] = user.user_id
        f.session["registration_date"] = user.registration_date
        # for key in f.session.keys():
        #     print(key)
        
        f.flash("Login successed!", "success")
        return f.render_template('index.html', logged_user_data = f.session)

@routes.route('/handle_register', methods=['POST'])
def handle_register():
    email_input_reg = f.request.form.get('email_input_reg')
    username_input_reg = f.request.form.get('username_input_reg')
    password_input_reg = f.request.form.get('password_input_reg')
    confirm_password_input_reg = f.request.form.get('confirm_password_input_reg')
    terms_conditions_input_reg = f.request.form.get('terms_conditions_input_reg')

    if not terms_conditions_input_reg:
        f.flash("You have to accept the terms and conditions", "warning")
        return f.render_template('register.html')

    if password_input_reg != confirm_password_input_reg:
        f.flash("Passwords don't match", "warning")
        return f.render_template('register.html')
    
    email_exists = db.session.query(User).filter_by(email=email_input_reg).first()
    if email_exists:
        f.flash("Email already exists", "warning")
        return f.render_template('register.html')
    
    username_exists = db.session.query(User).filter_by(username=username_input_reg).first()
    if username_exists:
        f.flash("Username already exists", "warning")
        return f.render_template('register.html')
    
    #if user can be added - add user
    user = User(email=email_input_reg, username=username_input_reg, password=password_input_reg)
    db.session.add(user)
    db.session.commit()
    
    return f.render_template('login.html')

@routes.route('/edit', methods=['POST'])
def edit():
    username_edit = f.request.form.get('username_edit')
    email_edit = f.request.form.get('email_edit')
    oldpassword_edit = f.request.form.get('oldpassword_edit')
    newpassword_edit = f.request.form.get('newpassword_edit')
    confirmpassword_edit = f.request.form.get('confirmpassword_edit')

    user = db.session.query(User).filter_by(email=f.session["email"]).first()
    if user:
        current_email = user.email
        current_username = user.username
        current_password = user.password

        if email_edit and current_email != email_edit:
            user.email = email_edit
            db.session.commit()

        if username_edit and current_username != username_edit:
            user.username = username_edit
            db.session.commit()

        if oldpassword_edit:
            if current_password == oldpassword_edit:
                if newpassword_edit:
                    if confirmpassword_edit and newpassword_edit == confirmpassword_edit:
                        user.password = newpassword_edit
                        db.session.commit()
                    else:
                        #has to be handled better
                        return "New and confirm passwords do not match"
                else:
                    #has to be handled better
                    return "You have to enter your new password"
            else:
                #has to be handled better
                return "Entered password doesn't match your current password"
            
        elif newpassword_edit or confirmpassword_edit:
            #has to be handled better
            return "You have to enter your old password"
    else:
        #this is a shadow realm. If user is here, something got fucked up
        print("No user")

    return f.render_template('user.html', logged_user_data = f.session)

@routes.route('/handle_logout', methods=['POST'])
def handle_logout():
    f.session.clear()
    return f.render_template('login.html')

@routes.route('/debug')
def show_tables():
    users = User.query.all()
    result = "<h2>Lista użytkowników</h2><ul>"
    for user in users:
        result += f"<li>ID: {user.user_id}, Username: {user.username}, Email: {user.email}</li>"
    result += "</ul>"
    return result

@routes.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = f.session["email"]
    if not user_id:
        return "Nie jesteś zalogowany"

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        f.session.clear()
        return f.redirect(f.url_for('home'))  
    
    return "Użytkownik nie istnieje"