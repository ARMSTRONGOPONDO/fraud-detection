from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User  # Import the User model

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to login if unauthorized
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# Load the user from the database by ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User class to integrate with Flask-Login
class UserModel(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.user_id = user.user_id
        self.password = user.password

# Login route
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user = User.query.filter_by(user_id=user_id).first()
        
        if user and check_password_hash(user.password, password):
            login_user(UserModel(user))
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to the main page
        else:
            flash('Invalid user ID or password.', 'danger')

    return render_template('login.html')  # Render login page

# Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))  # Redirect to login page
