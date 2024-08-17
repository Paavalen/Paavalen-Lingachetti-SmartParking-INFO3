import qrcode
import io
from flask import Blueprint, render_template, redirect, request, flash, url_for, jsonify
from flask_login import login_required, current_user
from .models import Parking, Reservation  
from . import db
from datetime import datetime, timedelta
from flask import send_file

views = Blueprint('views', __name__)

@views.route('/parking', methods=['GET'])
def parking():
    now = datetime.now().replace(microsecond=0)
    
    reservations = Reservation.query.all()
    for reservation in reservations:
        spot = Parking.query.get(reservation.spot_id)
        if spot and spot.state == 2 and reservation.isActive == 1 and reservation.end_time < now:
            spot.state = 1  # Set to free
            reservation.isActive = 0  # Set isActive to 0
            db.session.commit()

    parking_spots = Parking.query.all()
    return render_template("parking.html", user=current_user, parking_spots=parking_spots)

@views.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    parking_spots = Parking.query.all()
    
    if request.method == 'POST':
        spot_id = request.form.get('spot_id')
        start_time = request.form.get('start_time')
        hours = int(request.form.get('hours', 0))  # Get duration in hours

        start_time = datetime.fromisoformat(start_time)
        end_time = start_time + timedelta(hours=hours)

        now = datetime.now().replace(microsecond=0)

        isActive = 1 if start_time <= now < end_time else 0

        spot = Parking.query.get_or_404(spot_id)
        if spot.state != 1:
            flash('Spot is not available.', category='error')
            return redirect(url_for('views.parking'))

        reservation = Reservation(
            user_id=current_user.id,  
            spot_id=spot_id,
            start_time=start_time,
            end_time=end_time,
            isActive=isActive
        )
        db.session.add(reservation)
        
        spot.state = 2  # Reserved
        try:
            db.session.commit()
            flash('Reservation successful!', category='success')
            return redirect(url_for('views.parking'))
        except Exception as e:
            db.session.rollback()
            flash('Reservation failed. Please try again.', category='error')

    return render_template("book.html", user=current_user, parking_spots=Parking.query.all())

@views.route('/', methods=['GET'])
def home():
    return render_template("home.html", user=current_user)

@views.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if first_name:
            user.first_name = first_name

        if email:
            user.email = email

        if password:
            if password == confirm_password:
                user.set_password(password)  # Assuming you have a method to set the password
            else:
                flash('Passwords do not match.', category='error')
                return redirect(url_for('views.account'))

        try:
            db.session.commit()
            flash('Account updated successfully!', category='success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', category='error')

        return redirect(url_for('views.account'))

    return render_template("account.html", user=user)


@views.route('/my_reservations', methods=['GET'])
@login_required
def my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template("MyReservation.html", user=current_user, reservations=reservations)

@views.route('/generate_qr/<int:reservation_id>', methods=['GET'])
@login_required
def generate_qr(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('You do not have permission to generate a QR code for this reservation.', category='error')
        return redirect(url_for('views.my_reservations'))
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(reservation.id))
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Save QR code image to in-memory file
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@views.route('/extend_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def extend_reservation(reservation_id):
    # Logic to extend the reservation
    pass

@views.route('/cancel_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def cancel_reservation(reservation_id):
    # Logic to cancel the reservation
    pass