import flask as f
from routes import routes
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from models import User, Admin, GameResult, db
from flask_babel import Babel
import bcrypt

app = f.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

babel = Babel(app)
def hash_password(plain_password):
    """Haszuje hasło z użyciem bcrypt i soli."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def get_locale():
    return f.session.get('lang', 'en')

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

app.register_blueprint(routes) #dodaje zestaw tras (routes) do aplikacji

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        Admin.query.delete()
        User.query.delete()
        db.session.commit()

        test_user = User(
            username="testuser",
            email="testuser@gmail.com",
            password=hash_password("user123"),
            registration_date=datetime.now(timezone.utc)
        )
        db.session.add(test_user)

        test_admin = User(
            username="testadmin",
            email="testadmin@gmail.com",
            password=hash_password("admin123"),
            registration_date=datetime.now(timezone.utc)
        )
        db.session.add(test_admin)
        db.session.flush()
        db.session.add(Admin(user_id=test_admin.user_id))

        db.session.commit()

    app.run(debug=True)