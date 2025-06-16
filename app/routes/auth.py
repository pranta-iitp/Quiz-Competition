# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from app import db
from app.models import Users, Authors, Participants
from app.util import generate_user_id
from app.encryption_utils import encrypt_user_id, decrypt_user_id, encrypt_multiple_values, decrypt_multiple_values
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    return render_template('sign_in.html')

@auth_bp.route('/submit_sign_in', methods=['GET', 'POST'])
def submit_sign_in():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                flash('Please enter both email and password.', 'warning')
                return render_template('sign_in.html')

            try:
                user = Users.query.filter_by(user_email=email).first()
            except SQLAlchemyError as db_err:
                # Handle database errors
                flash('A database error occurred. Please try again later.', 'danger')
                # Optionally log db_err for debugging
                return render_template('sign_in.html')

            if user and user.user_password == password:
                session['user_id'] = user.user_id
                session['user_role'] = user.user_role
                session['user_name'] = user.user_name

                # Redirect based on role
                if user.user_role == 'admin':
                    return redirect(url_for('main.admin_dashboard'))
                elif user.user_role == 'superuser':
                    return redirect(url_for('main.superuser_dashboard'))
                elif user.user_role == 'author':
                    return redirect(url_for('author.dashboard')) 
                elif user.user_role == 'participant':
                    return redirect(url_for('participant.dashboard'))
                else:
                    flash('Unknown user role.', 'danger')
                    return redirect(url_for('auth.sign_in'))
            else:
                #flash('Login successful!', 'success')
                #flash('Invalid password', 'danger')
                flash('Invalid email or password. Try again', 'danger')
                return render_template('sign_in.html')

        return render_template('sign_in.html')

    except Exception as e:
        print(e)
        flash('An unexpected error occurred. Please try again later.', 'danger')
        return render_template('sign_in.html')


@auth_bp.route('/register_author', methods=['GET', 'POST'])
def register_author():
    if request.method == 'POST':
        # Handle JSON data
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Your existing logic
            user_id = generate_user_id()
            hashed_password = password  # Hash this properly!

            user = Users(
                user_id=user_id,
                user_name=username,
                user_email=email,
                user_password=hashed_password,
                user_role="author"
            )
            db.session.add(user)
            db.session.commit()
            
            author_id = generate_user_id()  
            author = Authors(
                author_id=author_id,
                author_user_id=user_id,
                author_name=None,
                author_email=email,
                author_subject_a=None,
                author_subject_b=None,
                author_subject_c=None,
                author_subject_d=None
            )
            db.session.add(author)
            db.session.commit()
           
            return jsonify({
                    'success': True,
                    'message': 'Author registered successfully!',
                    'user_id': user_id
                })
    # GET request - show the form
    return render_template('register_author.html')




@auth_bp.route('/register_participant', methods=['GET', 'POST'])
def register_participant():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Your existing logic
            user_id = generate_user_id()
            hashed_password = password  # Hash this properly!

            user = Users(
                user_id=user_id,
                user_name=username,
                user_email=email,
                user_password=hashed_password,
                user_role="participant"
            )
            db.session.add(user)
            db.session.commit()
        participant_id = generate_user_id()  
        # Create participant
        participant = Participants(
            participant_id=participant_id,
            participant_user_id=user_id,
            participant_name=None,
            participant_email=email,
            preferred_subject_a=None,
            preferred_subject_b=None,
            preferred_subject_c=None,
            preferred_subject_d=None
        )

        db.session.add(participant)
        db.session.commit()

        return jsonify({
                    'success': True,
                    'message': 'Participant registered successfully!',
                    'user_id': user_id
                })
    return render_template('register_participant.html')