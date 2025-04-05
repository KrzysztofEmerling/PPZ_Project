import flask as f
from models import User, db, Admin
from datetime import datetime, timezone

routes = f.Blueprint('routes', __name__)

@routes.route('/')
def home():
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    print("Zalogowany user_id:", user_id)
    print("Czy admin:", is_admin)
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
    
@routes.route('/admin_panel')
def admin_panel():
    uid = f.session.get("user_id")
    if not uid or not Admin.query.filter_by(user_id=uid).first():
        return "403 Forbidden", 403
    users = User.query.all()
    return f.render_template('admin.html', users=users)

@routes.route('/statistics')
def stats():
    return f.render_template('stats.html')
    
@routes.route('/my_games')
def history():
    return f.render_template('history.html')
    
@routes.route('/ranking')
def ranking():
    return f.render_template('ranking.html')


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

    email_exists_db = User.query.filter_by(email=email_input_login).first()
    username_exists_db = User.query.filter_by(email=email_input_login, password=password_input_login).first()

    if not email_exists_db:
        f.flash("Email doesn't exist in database!", "danger")
        return f.render_template('login.html', logged_user_data = f.session)
    
    elif not username_exists_db:
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
        return f.redirect(f.url_for('routes.home'))

@routes.route('/handle_register', methods=['POST'])
def handle_register():
    email_input_reg = f.request.form.get('email_input_reg')
    username_input_reg = f.request.form.get('username_input_reg')
    password_input_reg = f.request.form.get('password_input_reg')
    confirm_password_input_reg = f.request.form.get('confirm_password_input_reg')
    terms_conditions_input_reg = f.request.form.get('terms_conditions_input_reg')

    #I have more ideas of checking if email is valid, but who actually cares?
    #This code doesn't have to be perfect so let's not waste our time 
    #on this kind of bullshit

    #email is empty
    if email_input_reg == "":
        f.flash("Please enter Your email.", "warning")
        return f.render_template('register.html')

    #deletes spaces from the beginning and the end of username
    while email_input_reg[0] == " ":
        email_input_reg = email_input_reg[1:]

    while email_input_reg[-1] == " ":
        email_input_reg = email_input_reg[:-1]

    #email has capital letters
    if True in [a.isupper() for a in email_input_reg]:
        f.flash("Email cannot contain capital letters.", "warning")
        return f.render_template('register.html')

    #email dot not in text after @
    if "." not in email_input_reg.split("@")[-1]:
        f.flash("Email must contain top-level domain.", "warning")
        return f.render_template('register.html')

    #email nothing before @
    if email_input_reg[0] == "@":
        f.flash("Email must have characters before '@'.", "warning")
        return f.render_template('register.html')

    #username is empty
    if username_input_reg == "":
        f.flash("Please enter a username.", "warning")
        return f.render_template('register.html')

    #username is all spaces
    if all([char == " " for char in username_input_reg]):
        f.flash("All username characters are spaces.", "warning")

    #deletes spaces from the beginning and the end of username
    while username_input_reg[0] == " ":
        username_input_reg = username_input_reg[1:]

    while username_input_reg[-1] == " ":
        username_input_reg = username_input_reg[:-1]

    #password is empty
    if password_input_reg == "":
        f.flash("Please enter a password.", "warning")
        return f.render_template('register.html')

    #password contains a space
    if " " in password_input_reg:
        f.flash("Password must not contain spaces.", "warning")
        return f.render_template('register.html')
    
    #password contains less than 8 characters
    if len(password_input_reg) < 8:
        f.flash("Password has less than 8 characters.", "warning")
        return f.render_template('register.html')
    
    #password does not contain a lowercase letter
    if all([not char.islower() for char in password_input_reg]):
        f.flash("Password has no lowercase letters.", "warning")
        return f.render_template('register.html')
    
    #password does not contain a capital letter
    if all([not char.isupper() for char in password_input_reg]):
        f.flash("Password has no capital letters.", "warning")
        return f.render_template('register.html')
    
    #password does not contain a digit
    if all([not char.isdigit() for char in password_input_reg]):
        f.flash("Password has no digits.", "warning")
        return f.render_template('register.html')

    #password does not contain a special character
    if all([not char.isalnum() for char in password_input_reg]):
        f.flash("Password has no special characters.", "warning")
        return f.render_template('register.html')


    #stuff exists in database
    email_exists_db = db.session.query(User).filter_by(email=email_input_reg).first()
    if email_exists_db:
        f.flash("Email already exists.", "warning")
        return f.render_template('register.html')

    username_exists_db = db.session.query(User).filter_by(username=username_input_reg).first()
    if username_exists_db:
        f.flash("Username already exists.", "warning")
        return f.render_template('register.html')

    if password_input_reg != confirm_password_input_reg:
        f.flash("Passwords don't match.", "warning")
        return f.render_template('register.html')

    #terms and conditions not accepted
    if not terms_conditions_input_reg:
        f.flash("You have to accept the terms and conditions.", "warning")
        return f.render_template('register.html')

    try:
        #user can be now legally added - add user
        user = User(email=email_input_reg, username=username_input_reg, password=password_input_reg)
        db.session.add(user)
        db.session.commit()
        f.flash("Register successed. You can log in.", "success")
    except:
        #shadow realm, user should never see this
        f.flash("Register failed", "warning")
    
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