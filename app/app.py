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
        Admin.query.delete()
        User.query.delete()
        db.session.commit()

        test_user = User(
            username="testuser",
            email="testuser@gmail.com",
            password="user123",
            registration_date=datetime.now(timezone.utc)
        )
        db.session.add(test_user)

        test_admin = User(
            username="testadmin",
            email="testadmin@gmail.com",
            password="admin123",
            registration_date=datetime.now(timezone.utc)
        )
        db.session.add(test_admin)
        db.session.flush()
        db.session.add(Admin(user_id=test_admin.user_id))

        db.session.commit()

    app.run(debug=True)