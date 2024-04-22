from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/api/users/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))  # Redirect to home page if already logged in

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next') or url_for('views.home')
            return redirect(next_page)
        else:
            flash('Incorrect email or password. Please try again.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/api/users/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/api/users/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))  # Redirect to home page if already logged in

    if request.method == 'POST':
        user_type = request.form.get('user_type').lower()
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', category='error')
        elif user_type not in ['lender', 'borrower']:
            flash('Invalid user type', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            user = User(user_type=user_type, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Registration successful! Please log in.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("register.html", user=current_user)
