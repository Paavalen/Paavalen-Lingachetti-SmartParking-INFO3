from flask import Blueprint, render_template, redirect, request, flash, url_for, jsonify, send_file
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Parking, Reservation, User
from . import db
from datetime import datetime, timedelta
import qrcode
import io
from . import ser 

views = Blueprint('views', __name__)

@views.route('/parking', methods=['GET', 'POST'])
@login_required
def parking():
    if request.method == 'POST':
        try:
            data = request.get_json()
            spot_id = data.get('spot_id')
            state = data.get('state')

            if spot_id is None or state is None:
                return jsonify({'error': 'Invalid data'}), 400

            spot = Parking.query.get(spot_id)
            if spot:
                spot.state = state
                db.session.commit()

                if ser and ser.is_open:
                    if state == 2:  
                        ser.write(f"reserve:{spot_id}\n".encode())
                    elif state == 1:  
                        ser.write(f"free:{spot_id}\n".encode())
                    elif state == 3:  
                        ser.write(f"occupied:{spot_id}\n".encode())

                return jsonify({'message': 'Parking spot updated and state sent to Arduino'}), 200
            else:
                return jsonify({'error': 'Parking spot not found'}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    now = datetime.now().replace(microsecond=0)
    
    reservations = Reservation.query.all()
    for reservation in reservations:
        spot = Parking.query.get(reservation.spot_id)
        if spot and spot.state == 2 and reservation.isActive == 1 and reservation.end_time < now:
            spot.state = 1  
            reservation.isActive = 0
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
        hours = int(request.form.get('hours', 0))  
        
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
        
        spot.state = 2 
        try:
            db.session.commit()
            flash('Reservation successful!', category='success')
            
            return redirect(url_for('views.parking'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', category='error')

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
                user.password = generate_password_hash(password, method='pbkdf2:sha256') 
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
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.start_time.desc()).all()
    return render_template("MyReservation.html", user=current_user, reservations=reservations)

@views.route('/generate_qr/<int:reservation_id>', methods=['GET'])
@login_required
def generate_qr(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('You do not have permission to generate a QR code for this reservation.', category='error')
        return redirect(url_for('views.my_reservations'))
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(reservation.id))
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@views.route('/extend_reservation', methods=['POST'])
@login_required
def extend_reservation():
    try:
        reservation_id = request.form.get('reservation_id')
        additional_hours = int(request.form.get('additional_hours', 0))

        print(f"Received data - Reservation ID: {reservation_id}, Additional Hours: {additional_hours}")

        if additional_hours <= 0:
            return jsonify({'success': False, 'message': 'Additional hours must be greater than zero.'}), 400

        reservation = Reservation.query.get_or_404(reservation_id)

        if reservation.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'You do not have permission to extend this reservation.'}), 403

        reservation.end_time += timedelta(hours=additional_hours)
        db.session.commit()

        print("Reservation extended successfully")
        return jsonify({'success': True, 'message': 'Reservation extended successfully!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error extending reservation: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while extending the reservation.'}), 500

@views.route('/cancel_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('You do not have permission to cancel this reservation.', category='error')
        return redirect(url_for('views.my_reservations'))
    
    if request.method == 'POST':
        db.session.delete(reservation)
        
        spot = Parking.query.get(reservation.spot_id)
        if spot:
            spot.state = 1  
            db.session.commit()
            flash('Reservation cancelled successfully!', category='success')
        else:
            flash('Spot not found.', category='error')
        
        return redirect(url_for('views.my_reservations'))
    
    return redirect(url_for('views.my_reservations'))

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.parking'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@views.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('views.home'))

@views.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.parking'))

    return render_template("sign_up.html", user=current_user)
