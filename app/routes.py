import flask as f
from models import db, User, Admin, GameResult
from datetime import datetime, timezone
from sqlalchemy import func, inspect #func - potrzebna do napisania funkcji takich jak count(), distinct(), sum() itp.
from flask_babel import gettext as _
import bcrypt

routes = f.Blueprint('routes', __name__)

def hash_password(plain_password):
    """
    Haszuje hasło za pomocą algorytmu bcrypt z użyciem losowej soli.

    Args:
        plain_password (str): Hasło w postaci zwykłego tekstu.

    Returns:
        str: Zahasłowane hasło w postaci zakodowanego ciągu znaków.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(plain_password, hashed_password):
    """
    Sprawdza, czy podane hasło zgadza się z jego haszem.

    Args:
        plain_password (str): Hasło w postaci zwykłego tekstu.
        hashed_password (str): Hasło w postaci zahashowanej.

    Returns:
        bool: True jeśli hasła się zgadzają, False w przeciwnym razie lub w przypadku błędu dekodowania.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

# ============== obsługa zmiany jezykow ==============

@routes.route('/home/<lang>')
def home_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę główną.

    Args:
        lang (str): Kod języka do ustawienia (np. 'en', 'pl').

    Returns:
        Response: Renderowana strona główna z uwzględnieniem zaktualizowanych danych sesji i statusu administratora.
    """
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('index.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/login/<lang>')
def login_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę logowania.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona logowania z uwzględnieniem wybranego języka.
    """
    f.session['lang'] = lang
    return f.render_template('login.html')

@routes.route('/register/<lang>')
def register_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę rejestracji.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona rejestracji z uwzględnieniem wybranego języka.
    """
    f.session['lang'] = lang
    return f.render_template('register.html')

@routes.route('/user_panel/<lang>')
def user_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę profilu użytkownika.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona profilu użytkownika z uwzględnieniem wybranego języka i danych sesji.
    """
    f.session['lang'] = lang
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/edit_user/<lang>')
def edit_user_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę edycji danych użytkownika.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona edycji użytkownika z uwzględnieniem wybranego języka, danych sesji oraz informacji o edytowanym użytkowniku.
    """
    f.session['lang'] = lang
    reroute = f.request.form.get("reroute")
    edit_user_id = f.request.form.get("edit_user_id")
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('edit_user.html', logged_user_data = f.session, admin = is_admin, reroute = reroute, edit_user_id = edit_user_id)

@routes.route('/admin_panel/<lang>')
def admin_panel_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę panelu administracyjnego.

    Funkcja sprawdza, czy użytkownik jest administratorem. Jeśli tak, renderuje stronę panelu
    administracyjnego z listą użytkowników, którzy nie są administratorami. Jeśli użytkownik nie
    jest administratorem, zwraca odpowiedź 403 (Forbidden).

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona panelu administracyjnego z uwzględnieniem wybranego języka,
        danych sesji oraz listy użytkowników, którzy nie są administratorami. W przypadku braku
        uprawnień do panelu zwraca odpowiedź 403.
    """
    f.session['lang'] = lang
    uid = f.session.get("user_id")
    if not uid or not Admin.query.filter_by(user_id=uid).first():
        return "403 Forbidden", 403
    admin_user_ids = db.session.query(Admin.user_id)
    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)

@routes.route('/ranking/<lang>')
def ranking_set_lang(lang):
    """
    Ustawia preferowany język użytkownika i renderuje stronę z rankingiem najlepszych wyników.

    Funkcja umożliwia wyświetlenie rankingu najlepszych wyników dla określonego poziomu trudności.
    Ustawia również preferowany język użytkownika i sprawdza, czy użytkownik jest administratorem.
    Ranking jest ograniczony do pięciu najlepszych wyników na podstawie czasu ukończenia gry.
    Jeśli nie ma wyników dla wybranego poziomu trudności, wyświetlane jest odpowiednie ostrzeżenie.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona rankingu z najlepszymi wynikami, wybranym poziomem trudności
        oraz danymi użytkownika i administratorem (jeśli użytkownik jest administratorem).
    """
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
    """
    Ustawia preferowany język użytkownika i renderuje stronę z danymi statystyk dotyczącymi gier.

    Funkcja umożliwia wyświetlenie statystyk gier dla określonego poziomu trudności, w tym liczby gier, 
    liczby graczy, całkowitego czasu rozgrywek oraz czasu rozgrywek konkretnego użytkownika.
    Ustawia również preferowany język użytkownika i sprawdza, czy użytkownik jest administratorem.

    Args:
        lang (str): Kod języka do ustawienia (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona ze statystykami gier, z wybranym poziomem trudności oraz danymi
        użytkownika i administratorem (jeśli użytkownik jest administratorem).
    """
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
    """
    Ustawia preferowany język użytkownika i renderuje stronę z historią gier użytkownika.

    Funkcja sprawdza, czy użytkownik jest zalogowany, a następnie wyświetla historię gier tego użytkownika. 
    Jeżeli użytkownik nie jest zalogowany, zostanie przekierowany do strony logowania. Ustawia także preferowany język.

    Args:
        lang (str): Kod języka, który ma zostać ustawiony (np. 'pl', 'en').

    Returns:
        Response: Renderowana strona z historią gier użytkownika, lub przekierowanie na stronę logowania, 
        jeśli użytkownik nie jest zalogowany.
    """
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
    """
    Renderuje stronę główną aplikacji.

    Returns:
        str: Renderowany szablon strony głównej (`index.html`), z danymi o zalogowanym użytkowniku
            oraz jego uprawnieniach administracyjnych (jeśli są dostępne).        
    """
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('index.html', logged_user_data = f.session, admin = is_admin)

@routes.route('/edit_user', methods=['POST'])
def edit_user():
    """
    Wyświetla stronę profilu użytkownika.

    Funkcja pobiera dane użytkownika z sesji i sprawdza, czy użytkownik jest administratorem.
    Na podstawie tych danych renderuje stronę profilu użytkownika, przekazując informacje
    o zalogowanym użytkowniku oraz statusie administracyjnym do szablonu.

    Returns:
        str: Renderowany szablon strony profilu użytkownika (`user.html`), z danymi o 
             zalogowanym użytkowniku i jego uprawnieniach administracyjnych (jeśli dostępne).
    """
    reroute = f.request.form.get("reroute")
    edit_user_id = f.request.form.get("edit_user_id")
    user_id = f.session.get("user_id")
    is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
    return f.render_template('edit_user.html', logged_user_data = f.session, admin = is_admin, reroute = reroute, edit_user_id = edit_user_id)

@routes.route('/login')
def login():
    """
    Renderuje stronę logowania.

    Funkcja renderuje szablon strony logowania (`login.html`), umożliwiając użytkownikowi
    wprowadzenie danych logowania (np. nazwa użytkownika i hasło) oraz przesłanie formularza.

    Returns:
        str: Renderowany szablon strony logowania (`login.html`).
    """
    return f.render_template('login.html')

@routes.route('/register')
def register():
    """
    Renderuje stronę rejestracji.

    Funkcja renderuje szablon strony rejestracji (`register.html`), umożliwiając użytkownikowi
    wprowadzenie danych rejestracyjnych (np. nazwa użytkownika, hasło) i utworzenie nowego konta.

    Returns:
        str: Renderowany szablon strony rejestracji (`register.html`).
    """
    return f.render_template('register.html')
    
@routes.route('/admin_panel')
def admin_panel():
    """
    Renderuje panel administratora, umożliwiając zarządzanie użytkownikami.

    Funkcja sprawdza, czy użytkownik jest administratorem. Jeśli nie, zwraca odpowiedź 403 (Forbidden).
    Jeżeli użytkownik jest administratorem, renderuje stronę panelu administracyjnego, 
    wyświetlając listę użytkowników, którzy nie są administratorami.

    Returns:
        str: Renderowany szablon strony panelu administratora (`admin.html`), 
             zawierający listę użytkowników, którzy nie są administratorami.

    Raises:
        403 Forbidden: Jeśli użytkownik nie jest administratorem.
    """
    uid = f.session.get("user_id")
    if not uid or not Admin.query.filter_by(user_id=uid).first():
        return "403 Forbidden", 403
    admin_user_ids = db.session.query(Admin.user_id)
    non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
    return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)

@routes.route('/ranking')
def ranking():
    """
    Renderuje stronę z rankingiem najlepszych wyników w grze dla wybranego poziomu trudności.

    Funkcja sprawdza, czy użytkownik jest administratorem, a następnie pobiera najlepsze wyniki 
    (na podstawie najmniejszego czasu) dla danego poziomu trudności z bazy danych. Domyślnie 
    wyświetlany jest ranking dla poziomu 'easy', ale użytkownik może wybrać inny poziom trudności.
    Funkcja wyświetla ranking z najlepszymi wynikami (maksymalnie 5), a jeśli brak jest wyników 
    dla wybranego poziomu, wyświetla komunikat o braku dostępnych danych.

    Returns:
        str: Renderowany szablon strony z rankingiem (`ranking.html`), 
             zawierający dane o najlepszych wynikach dla wybranego poziomu trudności.
    """
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
    """
    Wyświetla statystyki gier na podstawie wybranego poziomu trudności.

    Funkcja pobiera dane dotyczące gier na wybranym poziomie trudności, takie jak liczba 
    gier, liczba graczy, łączny czas gry, oraz czas gry danego użytkownika. Statystyki są 
    wyświetlane na stronie z możliwością filtrowania po poziomie trudności. 

    Domyślny poziom trudności to "easy". Funkcja sprawdza, czy użytkownik jest administratorem, 
    a następnie wyświetla dane w odpowiednim szablonie HTML.

    Returns:
        Response: Zwraca odpowiedź HTTP z renderowanym szablonem HTML zawierającym statystyki 
        dla wybranego poziomu trudności oraz dane użytkownika, w tym łączny czas gry.
    """
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
    """
    Przekierowuje użytkownika na stronę profilu, jeśli jest zalogowany.

    Funkcja sprawdza, czy użytkownik posiada sesję (email i hasło). 
    Jeśli tak, renderuje stronę profilu z danymi sesji i informacją o uprawnieniach administratora. 
    W przeciwnym wypadku wyświetla komunikat o braku zalogowania i przekierowuje na stronę logowania.

    Returns:
        Response: Szablon HTML strony profilu użytkownika lub przekierowanie do strony logowania.
    """
    if "email" in f.session and "password" in f.session:
        user_id = f.session.get("user_id")
        is_admin = Admin.query.filter_by(user_id=user_id).first() is not None
        return f.render_template('user.html', logged_user_data = f.session, admin = is_admin)
    
    else:
        f.flash(_("You are not logged in."), "danger")
        return f.redirect(f.url_for('routes.login'))
    
@routes.route('/my_games', methods=['POST'])
def mygames_from_index():
    """
    Przekierowuje użytkownika na stronę historii gier, jeśli jest zalogowany.

    Funkcja sprawdza, czy użytkownik posiada aktywną sesję (na podstawie e-maila i hasła). 
    Jeżeli użytkownik jest zalogowany, renderuje stronę historii gier z danymi sesji oraz informacją, czy jest administratorem. 
    W przeciwnym wypadku wyświetla komunikat o braku zalogowania i przekierowuje na stronę logowania.

    Returns:
        Response: Szablon HTML historii gier użytkownika lub przekierowanie do strony logowania.
    """
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
    """
    Dodaje dostęp do folderu vendor z poziomu Flaska.

    Args:
        filename (str): Nazwa pliku w folderze vendor.

    Returns:
        Response: Obiekt odpowiedzi HTTP zawierający żądany plik.
    """
    return f.send_from_directory('vendor', filename)

@routes.route('/save_result', methods=['POST'])
def save_result():
    """
    Zapisuje nowy wynik gry do bazy danych.

    Obsługuje żądanie POST z danymi JSON zawierającymi ID użytkownika, poziom trudności,
    datę rozegrania gry i czas ukończenia. Normalizuje wartości poziomu trudności, konwertuje
    datę na obiekt typu datetime i zapisuje dane jako nowy wpis GameResult w bazie danych.

    Returns:
        Response: Obiekt JSON z informacją o powodzeniu ("success") lub błędzie ("error").
    """
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
    Sprawdza, czy podane hasło spełnia wymagania dotyczące bezpieczeństwa.

    Hasło musi mieć długość od 8 do 30 znaków, zawierać co najmniej jedną
    małą literę, jedną wielką literę, jedną cyfrę i jeden znak specjalny.
    Nie może zawierać spacji.

    Args:
        password (str): Hasło do sprawdzenia.

    Returns:
        bool: True jeśli hasło jest prawidłowe, w przeciwnym razie False.
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
    Poprawia format adresu e-mail i sprawdza jego poprawność.

    Waliduje e-mail pod względem długości, wielkości liter, obecności znaków
    przed i po znaku '@', oraz obecności domeny najwyższego poziomu.
    W razie błędu wyświetla stosowny komunikat za pomocą Flask `flash`.

    Args:
        email (str): Adres e-mail do sprawdzenia.

    Returns:
        list: [True, email] jeśli adres e-mail jest poprawny,
              [False, "EmailError"] lub [False, "UsernameError"] w przeciwnym razie.
    """
    #email is empty
    if email == "":
        f.flash(_("Please enter Your email."), "warning")
        return [False, "EmailError"]

    #deletes spaces from the beginning and the end of username
    email = email.strip()

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
    Usuwa nadmiarowe spacje i sprawdza poprawność nazwy użytkownika.

    Args:
        username (str): Nazwa użytkownika do sprawdzenia i korekty.

    Returns:
        list: [True, username] jeśli nazwa użytkownika jest poprawna, 
              lub [False, "UsernameError"] w przeciwnym wypadku.
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
    """
    Formatuje podaną liczbę sekund na bardziej czytelną formę (dni, godziny, minuty, sekundy).

    Funkcja przyjmuje liczbę sekund i konwertuje ją na format zawierający dni, godziny, minuty 
    oraz sekundy, w zależności od wartości wejściowej. Funkcja zwraca ciąg tekstowy reprezentujący
    czas w formacie "Xd Xh Xm Xs", gdzie X to liczba dni, godzin, minut lub sekund.

    Args:
        seconds (int): Liczba sekund do sformatowania.

    Returns:
        str: Sformatowany ciąg tekstowy przedstawiający czas w formie "Xd Xh Xm Xs".
             Przykład: "2d 3h 5m 30s" lub "5m 30s".

    Raises:
        ValueError: Jeśli `seconds` jest wartością, która nie może być przekonwertowana na liczbę.
    """    
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
    """
    Obsługuje logowanie użytkownika na podstawie wprowadzonego e-maila i hasła.

    Funkcja sprawdza, czy podany e-mail istnieje w bazie danych oraz czy hasło jest poprawne. 
    W przypadku błędnych danych logowania wyświetla odpowiednie komunikaty o błędach. 
    Jeśli dane są poprawne, zapisuje dane użytkownika w sesji i przekierowuje na stronę główną.

    Returns:
        Response: Szablon strony logowania z komunikatem błędu lub przekierowanie do strony głównej po udanym logowaniu.
    """
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
    """
    Obsługuje proces rejestracji użytkownika.

    Pobiera dane z formularza, waliduje je, sprawdza ich unikalność w bazie danych 
    i zapisuje nowego użytkownika z hasłem zakodowanym przez bcrypt. Obsługuje również 
    komunikaty o błędach i powodzeniu operacji.

    Returns:
        Response: Przekierowanie do odpowiedniego szablonu HTML w zależności od wyniku rejestracji.
    """
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

        user = User(email=email_input_reg, username=username_input_reg, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        f.flash(_("Register successed. You can log in."), "success")
    except:
        f.flash(_("Register failed."), "warning")
    
    return f.render_template('login.html')

@routes.route('/handle_logout', methods=['POST'])
def handle_logout():
    """
    Obsługuje proces wylogowania użytkownika.

    Czyści dane sesji użytkownika i przekierowuje do strony logowania z komunikatem.

    Returns:
        Response: Szablon logowania z komunikatem o sukcesie.
    """
    f.session.clear()
    f.flash(_("Logout successful."), "success")
    return f.render_template('login.html')

@routes.route('/edit', methods=['POST'])
def edit():
    """
    Obsługuje edycję danych użytkownika (zarówno przez użytkownika, jak i administratora).

    W zależności od źródła (panel użytkownika lub administratora), aktualizuje dane takie jak 
    nazwa użytkownika, e-mail i hasło. Przeprowadza walidację i odpowiednie zabezpieczenia 
    (np. konieczność podania starego hasła przez użytkownika). Obsługuje również sytuacje błędne.

    Returns:
        Response: Przekierowanie do odpowiedniego szablonu w zależności od źródła edycji oraz sukcesu/błędu.
    """
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
            return "Shadow realm wrong reroute data"

    else:
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
    """
    Usuwa użytkownika na podstawie przesłanego ID, z różnym zachowaniem w zależności od roli (admin/user).
    
    Oczekiwane pola formularza:
        - reroute: 'admin' lub 'user' (określa widok, do którego wrócić po usunięciu).
        - del_user_id: ID użytkownika do usunięcia.

    Jeśli użytkownik nie istnieje lub wystąpi inny problem — wyświetlana jest informacja ostrzegawcza.
    """
    reroute = f.request.form.get("reroute")
    del_user_id = f.request.form.get("del_user_id")
    print(del_user_id)
    user = User.query.get(del_user_id)

    if user:
        print("deleting user with id: ", del_user_id)
        print("user: ", user.username)

        if reroute == "admin":
            db.session.delete(user)
            db.session.commit()
            admin_user_ids = db.session.query(Admin.user_id)
            non_admin_users = User.query.filter(~User.user_id.in_(admin_user_ids)).all()
            return f.render_template('admin.html', non_admin_users=non_admin_users, logged_user_data = f.session)
        elif reroute == "user":
            db.session.delete(user)
            db.session.commit()
            f.session.clear()
            return f.redirect(f.url_for('routes.home'))
    else:
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