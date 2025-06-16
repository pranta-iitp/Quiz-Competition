from flask import Blueprint, render_template, redirect, url_for, flash, session

home_bp = Blueprint('home_bp', __name__)

@home_bp.route("/")
def home():
    return render_template('index.html')

@home_bp.route('/logout')
def logout_method():
    session.clear()
    flash('You have been logged out2.', 'success')
    return redirect(url_for('home_bp.home'))
