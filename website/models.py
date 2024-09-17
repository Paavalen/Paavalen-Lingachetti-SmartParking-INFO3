from .db import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Parking(db.Model):
    __tablename__ = 'parking'
    
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Integer, nullable=False)  
    reservations = db.relationship('Reservation', back_populates='parking_spot')

    def __repr__(self):
        return f'<Parking {self.id} - State {self.state}>'

class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=func.now())
    end_time = db.Column(db.DateTime)
    isActive = db.Column(db.Integer, nullable=False)  
    
    user = db.relationship('User', back_populates='reservations')
    parking_spot = db.relationship('Parking', back_populates='reservations')

    def __repr__(self):
        return f'<Reservation {self.id} - Spot {self.spot_id} for User {self.user_id}>'

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    
    reservations = db.relationship('Reservation', back_populates='user')

    def __repr__(self):
        return f'<User {self.id} - Email {self.email}>'
