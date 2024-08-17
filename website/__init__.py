from flask import Flask
from os import path
from flask_login import LoginManager
from .db import db  # Make sure this is where your db instance is
from .models import User, Parking, Reservation

DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Very Secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    
    from .views import views  # Import views blueprint
    app.register_blueprint(views, url_prefix='/')  # Register views blueprint

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'views.login'  # Updated to match the login route in views
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Create database and insert default data
    with app.app_context():
        create_database()

    return app

def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')

    if Parking.query.count() == 0:
        parking_spots = [Parking(state=1) for _ in range(4)]  # Adjust number as needed
        db.session.add_all(parking_spots)
        try:
            db.session.commit()
            print('Inserted default parking spots!')
        except Exception as e:
            db.session.rollback()
            print(f'Error inserting default parking spots: {e}')
