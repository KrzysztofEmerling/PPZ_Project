import flask as f
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

from datetime import datetime, timezone
from models import User, Admin, GameResult, db
from routes import routes

app = f.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "your_secret_key"

db.init_app(app)

app.register_blueprint(routes)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
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
