import flask as f
from models import db, User, Admin, GameResult
from datetime import datetime, timezone
from sqlalchemy import func, inspect #func - potrzebna do napisania funkcji takich jak count(), distinct(), sum() itp.
from flask_babel import gettext as _
import bcrypt

routes = f.Blueprint('routes', __name__)
def hash_password(plain_password):
    """Haszuje hasło z użyciem bcrypt i soli."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

# ============== obsługa zmiany jezykow ==============

@routes.route('/home/<lang>')
def home_set_lang(lang):
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('index.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/login/<lang>')
def login_set_lang(lang):
    f.session['lang'] = lang
    return f.render_template('login.html')

@routes.route('/register/<lang>')
def register_set_lang(lang):
    f.session['lang'] = lang
    return f.render_template('register.html')

@routes.route('/user_panel/<lang>')
def user_set_lang(lang):
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/edit_user/<lang>')
def edit_user_set_lang(lang):
    f.session['lang'] = lang
    reroute = f.request.form.get("reroute")
    edit_user_id = f.request.form.get("edit_user_id")
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('edit_user.html', logged_user_data = f.session, admin = is_admin, reroute = reroute, edit_user_id = edit_user_id)

@routes.route('/admin_panel/<lang>')
def admin_panel_set_lang(lang):
    f.session['lang'] = lang
    uid = f.session.get("user_id")
    if not uid or not Admin.query.filter_by(user_id=uid).first():
        return "403 Forbidden", 403
    admin_user_ids = db.session.query(Admin.user_id)
    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)

@routes.route('/ranking/<lang>')
def ranking_set_lang(lang):
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None

    #poziomy trudności - domyślnie 'easy'
    selected_difficulty = f.request.args.get("difficulty", "easy")
    difficulties = ['easy', 'intermediate', 'hard', 'expert']
    if selected_difficulty not in difficulties:
        selected_difficulty = 'easy'

    #pobranie najlepszych wyników (najmniejszy czas) dla wybranego poziomu trudności
    results = (
        db.session.query(GameResult, User.username)
        .join(User, GameResult.user_id == User.user_id)
        .filter(GameResult.difficulty == selected_difficulty)
        .order_by(GameResult.time_finished.asc())
        .limit(5)
        .all()
    )

    #brak gier dla wybranego poziomu trudności
    if not results:
        f.flash(f'Ranking not available for this level yet!', 'warning')

    #przygotowanie danych do wyświetlenia
    ranking_data = []
    for idx, (game, username) in enumerate(results, start=1):
        ranking_data.append({
            'place': idx,
            'username': username,
            'difficulty': game.difficulty,
            'time': game.time_finished,
            'date': game.date_played.strftime('%Y-%m-%d')
        })

    return f.render_template('ranking.html', ranking_data=ranking_data, selected_difficulty=selected_difficulty, logged_user_data=f.session, admin=is_admin)

@routes.route('/statistics/<lang>')
def stats_set_lang(lang):
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None

    #poziomy trudności ; domyślnie - "easy"
    selected_difficulty = f.request.args.get("difficulty", "easy")
    difficulties = ['easy', 'intermediate', 'hard', 'expert']
    if selected_difficulty not in difficulties:
        selected_difficulty = 'easy'

    total_games = db.session.query(func.count(GameResult.result_id)).filter_by(difficulty=selected_difficulty).scalar() or 0

    #brak gier dla wybranego poziomu trudności
    if total_games == 0:
        f.flash(f'Statistics not available for this level yet!', 'warning')

    total_players = db.session.query(func.count(func.distinct(GameResult.user_id))).filter_by(difficulty=selected_difficulty).scalar() or 0

    total_playtime = db.session.query(func.sum(GameResult.time_finished)).filter_by(difficulty=selected_difficulty).scalar() or 0

    your_total_playtime = db.session.query(func.sum(GameResult.time_finished)).filter_by(difficulty=selected_difficulty, user_id=user_id).scalar() or 0

    return f.render_template('stats.html', logged_user_data=f.session, admin=is_admin, selected_difficulty=selected_difficulty, total_games=total_games, total_players=total_players, total_playtime=total_playtime, your_total_playtime=your_total_playtime)

@routes.route('/my_games/<lang>')
def mygames_set_lang(lang):
    f.session['lang'] = lang
    if "email" in f.session and "password" in f.session:
        user_id = f.session.get("user_id")
        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
        games = GameResult.query.filter_by(user_id=user_id).all()
        return f.render_template('history.html', logged_user_data = f.session, admin = is_admin, user_games = games)
    
    else:
        f.flash("You are not logged in", "danger")
        return f.redirect(f.url_for('routes.login'))

# ====================================================

# =========== poruszanie sie po aplikacji ============

@routes.route('/')
def home():
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('index.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/edit_user', methods=['POST'])
def edit_user():
    reroute = f.request.form.get("reroute")
    edit_user_id = f.request.form.get("edit_user_id")
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('edit_user.html', logged_user_data = f.session, admin = is_admin, reroute = reroute, edit_user_id = edit_user_id)

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
    admin_user_ids = db.session.query(Admin.user_id)
    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)

@routes.route('/ranking')
def ranking():
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None

    #poziomy trudności - domyślnie 'easy'
    selected_difficulty = f.request.args.get("difficulty", "easy")
    difficulties = ['easy', 'intermediate', 'hard', 'expert']
    if selected_difficulty not in difficulties:
        selected_difficulty = 'easy'

    #pobranie najlepszych wyników (najmniejszy czas) dla wybranego poziomu trudności
    results = (
        db.session.query(GameResult, User.username)
        .join(User, GameResult.user_id == User.user_id)
        .filter(GameResult.difficulty == selected_difficulty)
        .order_by(GameResult.time_finished.asc())
        .limit(5)
        .all()
    )

    #brak gier dla wybranego poziomu trudności
    if not results:
        f.flash(f'{_("Ranking not available for this level yet!")}', 'warning')

    #przygotowanie danych do wyświetlenia
    ranking_data = []
    for idx, (game, username) in enumerate(results, start=1):
        ranking_data.append({
            'place': idx,
            'username': username,
            'difficulty': game.difficulty,
            'time': format_seconds(game.time_finished),
            'date': game.date_played.strftime('%Y-%m-%d')
        })

    return f.render_template('ranking.html', ranking_data=ranking_data, selected_difficulty=selected_difficulty, logged_user_data=f.session, admin=is_admin)

@routes.route('/statistics')
def stats():
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None

    #poziomy trudności ; domyślnie - "easy"
    selected_difficulty = f.request.args.get("difficulty", "easy")
    difficulties = ['easy', 'intermediate', 'hard', 'expert']
    if selected_difficulty not in difficulties:
        selected_difficulty = 'easy'

    total_games = db.session.query(func.count(GameResult.result_id)).filter_by(difficulty=selected_difficulty).scalar() or 0

    #brak gier dla wybranego poziomu trudności
    if total_games == 0:
        f.flash(f'{_("Statistics not available for this level yet!")}', 'warning')

    total_players = db.session.query(func.count(func.distinct(GameResult.user_id))).filter_by(difficulty=selected_difficulty).scalar() or 0

    total_playtime = db.session.query(func.sum(GameResult.time_finished)).filter_by(difficulty=selected_difficulty).scalar() or 0

    your_total_playtime = db.session.query(func.sum(GameResult.time_finished)).filter_by(difficulty=selected_difficulty, user_id=user_id).scalar() or 0

    return f.render_template('stats.html', logged_user_data=f.session, admin=is_admin, selected_difficulty=selected_difficulty, total_games=total_games, total_players=total_players, total_playtime=total_playtime, your_total_playtime=your_total_playtime)

@routes.route('/user_panel', methods=['POST'])
def myprof_from_index():
    if "email" in f.session and "password" in f.session:
        user_id = f.session.get("user_id")
        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
        return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
    
    else:
        f.flash(_("You are not logged in."), "danger")
        return f.redirect(f.url_for('routes.login'))
    
@routes.route('/my_games', methods=['POST'])
def mygames_from_index():
    if "email" in f.session and "password" in f.session:
        user_id = f.session.get("user_id")
        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
        games = GameResult.query.filter_by(user_id=user_id).all()
        return f.render_template('history.html', logged_user_data = f.session, admin = is_admin, user_games = games)
    
    else:
        f.flash(_("You are not logged in."), "danger")
        return f.redirect(f.url_for('routes.login'))

# ====================================================

# ================ logika aplikacji ==================

@routes.route('/vendor/<path:filename>')
def serve_vendor(filename):
    return f.send_from_directory('vendor', filename)

@routes.route('/save_result', methods=['POST'])
def save_result():
    try:
        data = f.request.get_json()
        id = data.get("user_id")
        diff = data.get("difficulty")
        date = data.get("date_played")
        time = data.get("time_finished")

        if date.endswith('Z'):
            date = date[:-1]

        if diff == 'medium':
            diff = 'intermediate'
        
        if diff == 'diabolical':
            diff = 'expert'

        datetime_object = datetime.fromisoformat(date)
        finaldate = datetime_object.replace(microsecond=0)

        #print(f"id: {id}, difficulty: {diff}, date: {date}, time: {time}")

        game_data = GameResult(user_id = id, difficulty = diff, date_played = finaldate, time_finished = time)
        db.session.add(game_data)
        db.session.commit()
        
        return f.jsonify({"status": "success", "message": "Dane zapisane pomyślnie"})
    
    except Exception as e:
        return f.jsonify({"status": "error", "message": str(e)}), 500

def is_password_alright(password):
    """
    Checks if password is valid.

    Args:
        password (str): Password to check.

    Returns:
        bool: True if password is valid, False otherwise.
    """
    #password is empty
    if password == "":
        f.flash(_("Please enter a password."), "warning")
        return False

    #password contains a space
    elif " " in password:
        f.flash(_("Password must not contain spaces."), "warning")
        return False
    
    #password contains less than 8 characters
    elif len(password) < 8:
        f.flash(_("Password has less than 8 characters."), "warning")
        return False
    
    elif len(password) > 30:
        f.flash(_("Password cannot have more than 30 characters."), "warning")
        return False
    
    #password does not contain a lowercase letter
    elif all([not char.islower() for char in password]):
        f.flash(_("Password has no lowercase letters."), "warning")
        return False
    
    #password does not contain a capital letter
    elif all([not char.isupper() for char in password]):
        f.flash(_("Password has no capital letters."), "warning")
        return False
    
    #password does not contain a digit
    elif all([not char.isdigit() for char in password]):
        f.flash(_("Password has no digits."), "warning")
        return False

    #password does not contain a special character
    elif all([not char.isalnum() for char in password]):
        f.flash(_("Password has no special characters."), "warning")
        return False

    return True

def email_validator_corrector(email):
    """
    Corrects email and checks if it is valid.

    Args:
        email (str): Email to check.

    Returns:
        return [True, email] if email is valid, [False, "EmailError"] otherwise
    """
    #email is empty
    if email == "":
        f.flash(_("Please enter Your email."), "warning")
        return [False, "EmailError"]

    #deletes spaces from the beginning and the end of username
    email.strip()

    #email has capital letters
    if True in [a.isupper() for a in email]:
        f.flash(_("Email cannot contain capital letters."), "warning")
        return [False, "EmailError"]

    #email dot not in text after @
    if "." not in email.split("@")[-1]:
        f.flash(_("Email must contain top-level domain."), "warning")
        return [False, "EmailError"]

    #email nothing before @
    if email[0] == "@":
        f.flash(_("Email must have characters before '@'."), "warning")
        return [False, "EmailError"]

    if len(email) > 100:
        f.flash(_("Email must be 100 characters or fewer."), "warning")
        return [False, "UsernameError"]

    return [True, email]

def username_validator_corrector(username):
    """
    Corrects username and checks if it is valid.

    Args:
        username (str): Username to check.

    Returns:
        return [True, username] if username is valid, [False, "UsernameError"] otherwise
    """
    #username is empty
    if username == "":
        f.flash("Please enter a username.", "warning")
        return [False, "UsernameError"]

    #username is all spaces
    if username.isspace():
        f.flash("All username characters are spaces.", "warning")
        return [False, "UsernameError"]

    #deletes spaces from the beginning and the end of username
    username = username.strip()

    if len(username) < 3:
        f.flash("Username must be 3 characters or more.", "warning")
        return [False, "UsernameError"]

    if len(username) > 32:
        f.flash("Username must be 32 characters or fewer.", "warning")
        return [False, "UsernameError"]

    return [True, username]

#format ilości godzin dla Statystyk
@routes.app_template_filter('format_seconds')
def format_seconds(seconds):
    if not seconds:
        return "0s"
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)

@routes.route('/handle_login', methods=['POST'])
def handle_login():
    email_input_login = f.request.form.get('email_input_login')
    password_input_login = f.request.form.get('password_input_login')

    email_entity = User.query.filter_by(email=email_input_login).first()
    
    if not email_entity:
        f.flash(_("Email doesn't exist in database!"), "danger")
        return f.render_template('login.html', logged_user_data = f.session)

    if not check_password(password_input_login, email_entity.password):
        f.flash(_("Wrong password!"), "danger")
        return f.render_template('login.html', logged_user_data=f.session) 

    # email exists in database and password matches the hashed one
    # - can proceed with login process
    f.session["email"] = email_input_login
    f.session["password"] = email_entity.password
    f.session["username"] = email_entity.username
    f.session["user_id"] = email_entity.user_id
    f.session["registration_date"] = email_entity.registration_date
    # for key in f.session.keys():
    #     print(key)
    
    f.flash(_("Login successed!"), "success")
    return f.redirect(f.url_for('routes.home'))
    
@routes.route('/handle_register', methods=['POST'])
def handle_register():
    email_input_reg = f.request.form.get('email_input_reg')
    username_input_reg = f.request.form.get('username_input_reg')
    password_input_reg = f.request.form.get('password_input_reg')
    confirm_password_input_reg = f.request.form.get('confirm_password_input_reg')
    terms_conditions_input_reg = f.request.form.get('terms_conditions_input_reg')

    #check data validity
    email_validator = email_validator_corrector(email_input_reg)
    if not email_validator[0]:
        return f.render_template('register.html')
    else:
        email_input_reg = email_validator[1]

    username_validator = username_validator_corrector(username_input_reg)
    if not username_validator[0]:
        return f.render_template('register.html')
    else:
        username_input_reg = username_validator[1]

    if not is_password_alright(password_input_reg):
        return f.render_template('register.html')

    #check if stuff exists in database
    email_exists_db = db.session.query(User).filter_by(email=email_input_reg).first()
    if email_exists_db:
        f.flash(_("Email already exists."), "warning")
        return f.render_template('register.html')

    username_exists_db = db.session.query(User).filter_by(username=username_input_reg).first()
    if username_exists_db:
        f.flash(_("Username already exists."), "warning")
        return f.render_template('register.html')

    if password_input_reg != confirm_password_input_reg:
        f.flash(_("Passwords don't match."), "warning")
        return f.render_template('register.html')

    #terms and conditions not accepted
    if not terms_conditions_input_reg:
        f.flash(_("You have to accept the terms and conditions."), "warning")
        return f.render_template('register.html')

    try:
        #hashed password to be saved into database
        hashed_password = hash_password(password_input_reg)

        #user can be now legally added - add user with hashed password
        user = User(email=email_input_reg, username=username_input_reg, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        f.flash(_("Register successed. You can log in."), "success")
    except:
        #shadow realm, user should never see this
        f.flash(_("Register failed."), "warning")
    
    return f.render_template('login.html')

@routes.route('/handle_logout', methods=['POST'])
def handle_logout():
    f.session.clear()
    f.flash(_("Logout successful."), "success")
    return f.render_template('login.html')

@routes.route('/edit', methods=['POST'])
def edit():
    reroute = f.request.form.get("reroute")
    edit_user_id = f.request.form.get("edit_user_id")

    username_edit = f.request.form.get('username_edit')
    email_edit = f.request.form.get('email_edit')
    #old password only needed if editing yourself from user panel
    oldpassword_edit = f.request.form.get('oldpassword_edit')
    newpassword_edit = f.request.form.get('newpassword_edit')
    confirmpassword_edit = f.request.form.get('confirmpassword_edit')

     # if everything is empty
    if (username_edit == "" and 
        email_edit == "" and 
        oldpassword_edit == "" and 
        newpassword_edit == "" and 
        confirmpassword_edit == ""):
        f.flash(_("Input data to edit."), "warning")
        if reroute == "user":
            user_id = f.session.get("user_id")
            is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
            return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
        elif reroute == "admin":
            admin_user_ids = db.session.query(Admin.user_id)
            non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
            return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
        else:
            return "Shadow realm"

    user = User.query.get(edit_user_id)
    if user:
        edit_user_email = user.email
        edit_user_username = user.username
        edit_user_password = user.password
        print("User exists")

        #if username was input and doesn't match users username
        if username_edit != "" and edit_user_username != username_edit:
            if not username_validator_corrector(username_edit)[0]:
                if reroute == "user":
                    user_id = f.session.get("user_id")
                    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                    return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
                elif reroute == "admin":
                    admin_user_ids = db.session.query(Admin.user_id)
                    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
                    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
                else:
                    return "Shadow realm"
            else:
                username_edit = username_validator_corrector(username_edit)[1]
                user.username = username_edit
                f.session["username"] = username_edit
                db.session.commit()
                print("Username changed")
                print(user.username)

        print("Back from username block")

        #if email was input and doesn't match users email
        if email_edit != "" and edit_user_email != email_edit:
            if not email_validator_corrector(email_edit)[0]:
                if reroute == "user":
                    user_id = f.session.get("user_id")
                    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                    return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
                elif reroute == "admin":
                    admin_user_ids = db.session.query(Admin.user_id)
                    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
                    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
                else:
                    return "Shadow realm"
            else:
                email_edit = email_validator_corrector(email_edit)[1]
                user.email = email_edit
                f.session["email"] = email_edit
                db.session.commit()


        if reroute == "user":
            #if old password was input...
            if oldpassword_edit != "":
                #if old password matches
                if check_password(oldpassword_edit, edit_user_password):
                    print("Password is correct")
                    #if new password was input...
                    if newpassword_edit != "":
                        if is_password_alright(newpassword_edit):
                            #if confirm password was input and matches new password
                            if confirmpassword_edit and newpassword_edit == confirmpassword_edit:
                                hashed_password = hash_password(newpassword_edit)
                                print(f"Zahashowane nowe hasło: {hashed_password}")
                                user.password = hashed_password
                                f.session["password"] = hashed_password
                                db.session.commit()
                            else:
                                f.flash(_("New and confirm passwords do not match."), "warning")
                                user_id = f.session.get("user_id")
                                is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                                return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
                        else:
                            #flashing already handled
                            user_id = f.session.get("user_id")
                            is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                            return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
                    else:
                        f.flash(_("You have to enter new password."), "warning")
                        user_id = f.session.get("user_id")
                        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                        return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
                else:
                    f.flash(_("Entered password doesn't match your current password."), "warning")
                    user_id = f.session.get("user_id")
                    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                    return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
            #old password was not input, if new or confirmed one was input.
            elif newpassword_edit != "" or confirmpassword_edit != "":
                f.flash(_("You have to enter your old password first."), "warning")
                user_id = f.session.get("user_id")
                is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
                return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)

        elif reroute == "admin":
            #if new password was input...
            if newpassword_edit != "":
                #improve password checking here!
                if is_password_alright(newpassword_edit):
                    #if confirm password was input and matches new password
                    if confirmpassword_edit and newpassword_edit == confirmpassword_edit:
                        user.password = newpassword_edit
                        db.session.commit()
                    else:
                        f.flash(_("New and confirm passwords do not match."), "warning")
                        admin_user_ids = db.session.query(Admin.user_id)
                        non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
                        return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
                else:
                    #flashing already handled
                    admin_user_ids = db.session.query(Admin.user_id)
                    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
                    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
            elif confirmpassword_edit != "":
                f.flash(_("Enter new password before confirming."), "warning")
                admin_user_ids = db.session.query(Admin.user_id)
                non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
                return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
        else:
            # shadow realm. App works incorrectly. 
            # Data passed should not me anything different, ever
            return "Shadow realm wrong reroute data"

    else:
        #this is a shadow realm.
        #user shown in list MUST exist.
        return "Shadow realm no reroute"
     
    if reroute == "user":
        user_id = f.session.get("user_id")
        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
        return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
    elif reroute == "admin":
        admin_user_ids = db.session.query(Admin.user_id)
        non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
        return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)

@routes.route('/delete_user', methods=['POST'])
def delete_user():
    reroute = f.request.form.get("reroute")
    del_user_id = f.request.form.get("del_user_id")
    print(del_user_id)

    # user_id = f.session["email"]
    # if not user_id:
    #     #shadow realm in end program
    #     f.flash("You are not logged in.", "warning")
    #     if reroute == "admin":
    #         admin_user_ids = db.session.query(Admin.user_id)
    #         non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
    #         return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
    #     elif reroute == "user":
    #         return f.render_template('user.html', logged_user_data = f.session)
    #     else:
    #         print("ERROR IS HAPPENING. YOU ARE IN SHADOW REALM - WRONG REROUTE")
    #         return f.redirect(f.url_for('home'))

    user = User.query.get(del_user_id)
    if user:
        print("deleting user with id: ", del_user_id)
        print("user: ", user.username)

        if reroute == "admin":
            db.session.delete(user)
            db.session.commit()
            # f.session.clear()
            admin_user_ids = db.session.query(Admin.user_id)
            non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
            return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
        elif reroute == "user":
            db.session.delete(user)
            db.session.commit()
            f.session.clear()
            return f.redirect(f.url_for('routes.home'))
    else:
        #shadow realm, but handled with care and love. Quoting Donald Knuth:
        #"A well-written program should fail gracefully."
        print("ERROR IS HAPPENING. YOU ARE IN SHADOW REALM - NO USER")
        f.flash(_("User does not exist."), "warning")

        if reroute == "admin":
            admin_user_ids = db.session.query(Admin.user_id)
            non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
            return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
        elif reroute == "user":
            user_id = f.session.get("user_id")
            is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
            return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
            # return f.render_template('user.html', logged_user_data = f.session)
        else:
            print("ERROR IS HAPPENING. YOU ARE IN SHADOW REALM - WRONG REROUTE")
            return f.redirect(f.url_for('routes.home'))
        
# ====================================================

# =============== funkcje debugujace =================

@routes.route('/debug')
def show_tables():
    users = User.query.all()
    result = "<h2>Lista użytkowników</h2><ul>"
    for user in users:
        result += f"<li>ID: {user.user_id}, Username: {user.username}, Email: {user.email}</li>"
    result += "</ul>"
    return result

# ====================================================