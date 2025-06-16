# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for, flash, session

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template('index.html')

@main_bp.route('/logout')
def logout_method():
    session.clear()  # Clear all session data
    flash('You have been logged out3.', 'success')
    return redirect(url_for('main.home'))  # Redirect to home page

@main_bp.route("/create_quiz")
def create_quiz():
    return render_template('index.html')

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main_bp.route('/superuser/dashboard')
def superuser_dashboard():
    return render_template('superuser_dashboard.html')