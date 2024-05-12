from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..database import db
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User, UserType

from werkzeug.security import generate_password_hash, check_password_hash
import logging

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Constants
MIN_EMAIL_LENGTH = 4
MIN_PASSWORD_LENGTH = 7

@auth.route('/api/users/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You are already registered and logged in.", category='info')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        return handle_register_post()

    return render_template("register.html", user=current_user)
    
def handle_register_post():
    print("Received form data:", request.form)

    user_type_id = request.form.get('user_type_id')
    if user_type_id == 'lender':
        user_type_id = 1
    else:
        user_type_id = 2
    if user_type_id is None:
        flash('User type is required.', category='error')
        return render_template("register.html", user=current_user)

    try:
        user_type_id = int(user_type_id)
    except ValueError:
        flash('Invalid user type.', category='error')
        return render_template("register.html", user=current_user)

    email = request.form.get('email')
    password = request.form.get('password')

    if not is_valid_registration(user_type_id, email, password):
        return render_template("register.html", user=current_user)

    user = User(user_type_id=user_type_id, email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256'))
    db.session.add(user)
    db.session.commit()
    flash('Registration successful! Please log in.', category='success')
    return redirect(url_for('auth.login'))

def is_valid_registration(user_type_id, email, password):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already exists!', category='error')
        return False
    if user_type_id not in [UserType.LENDER, UserType.BORROWER]:
        flash('Invalid user type', category='error')
        return False
    if len(email) < MIN_EMAIL_LENGTH:
        flash('Email must be greater than 3 characters', category='error')
        return False
    if len(password) < MIN_PASSWORD_LENGTH:
        flash('Password must be at least 7 characters.', category='error')
        return False
    return True

@auth.route('/api/users/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    logger.debug(f"Current user authenticated: {current_user.is_authenticated}")

    if request.method == 'POST':
        return handle_login_post()

    return render_template('login.html')

def handle_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=True)
        logger.debug("Login successful")
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('views.home'))
    
    flash('Invalid email or password. Please try again.', category='error')
    return render_template('login.html')

@auth.route('/api/users/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))