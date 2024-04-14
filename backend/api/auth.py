from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models import User
from ..database import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/api/users/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', category='error')
            return redirect(url_for('auth.login'))
        
        flash('Logged in Successfully', category='success')
        return redirect(url_for('views.home'))
    return render_template('login.html')


@auth.route('/api/users/logout')
def logout():
    # Implement logout functionality if needed
    flash('Logged out Successfully', category='success')
    return redirect(url_for('views.home'))  # Redirect to home page after logout


@auth.route('/api/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type').lower()
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', category='error')
            return redirect(url_for('auth.register'))  # Redirect back to registration page

        # Validate user type
        if user_type not in ['lender', 'borrower']:
            flash('Invalid user type', category='error')
            return redirect(url_for('auth.register'))  # Redirect back to registration page
        
        # Validate email and password
        if len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
            return redirect(url_for('auth.register'))  # Redirect back to registration page
        if len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.register'))  # Redirect back to registration page

        # Create new user
        new_user = User(user_type=user_type, email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        # Redirect based on user type
        '''
        if user_type == 'lender':
            flash('User registered successfully as Lender', category='success')
            return redirect(url_for('views.add_resource'))
        elif user_type == 'borrower':
            flash('User registered successfully as Borrower', category='success')
            return redirect(url_for('views.submit_request'))'''

    # Render the registration form template
    return render_template("register.html")
