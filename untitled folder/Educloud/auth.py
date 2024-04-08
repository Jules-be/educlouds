from flask import Blueprint, render_template, request, flash, redirect, url_for

auth = Blueprint('auth', __name__)

@auth.route('/api/users/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template('login.html', boolean=True)

@auth.route('/api/users/logout')
def logout():
    return "<p>logout</p>"

@auth.route('/api/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('userType')
        email = request.form.get('email')
        password1 = request.form.get('password')
        
        # Check validations 
        if user_type not in ['Lender', 'Borrower']:
            flash('Invalid user type', category='error')
        if len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        if len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            flash('User registered successfully', category='success')
            
            if user_type == 'Lender':
                return redirect(url_for('views.submit_request'))
            elif user_type == 'Borrower':
                return redirect(url_for('views.add_resource'))
        # Redirect to the register page to display flashed messages

    # Render the registration form template
    return render_template("register.html")
