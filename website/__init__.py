from flask import Flask
from os import path
from flask_login import LoginManager
from .db import db 
from .models import User, Parking, Reservation
import serial
import threading
import time

DB_NAME = "database.db"

ser = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Very Secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views 
    app.register_blueprint(views, url_prefix='/') 

    login_manager = LoginManager()
    login_manager.login_view = 'views.login' 
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    with app.app_context():
        create_database()

    initialize_serial()
    start_background_thread(app)  

    return app

def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')

    if Parking.query.count() == 0:
        parking_spots = [Parking(state=1) for _ in range(4)] 
        db.session.add_all(parking_spots)
        try:
            db.session.commit()
            print('Inserted default parking spots!')
        except Exception as e:
            db.session.rollback()
            print(f'Error inserting default parking spots: {e}')

def initialize_serial():
    global ser
    try:
        ser = serial.Serial('COM9', 115200, timeout=1) 
        print("Serial port initialized")
    except Exception as e:
        print(f"Failed to initialize serial: {e}")
        ser = None

def monitor_parking_state(app):
    while True:
        with app.app_context():
            from .models import Parking  
            parking_spots = Parking.query.all() 
            for spot in parking_spots:
                if spot.state == 2: 
                    if ser and ser.is_open:
                        ser.write(f"reserve:{spot.id}\n".encode())
                        print(f"Sent to Arduino: reserve:{spot.id}")
                elif spot.state == 1:  
                    if ser and ser.is_open:
                        ser.write(f"free:{spot.id}\n".encode())
                        print(f"Sent to Arduino: free:{spot.id}")
                elif spot.state == 3:  
                    if ser and ser.is_open:
                        ser.write(f"occupied:{spot.id}\n".encode())
                        print(f"Sent to Arduino: free:{spot.id}")
        time.sleep(1) 

def start_background_thread(app):
    thread = threading.Thread(target=monitor_parking_state, args=(app,))
    thread.daemon = True  
    thread.start()
    

