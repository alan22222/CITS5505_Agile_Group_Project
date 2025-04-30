from flask import render_template, redirect, url_for, request
from . import app

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # For now, just redirect to upload page without checking credentials
        return redirect(url_for('upload'))
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Handle the form submission here
        file = request.files.get('file')
        text = request.form.get('text')
        print(f"Received file: {file.filename if file else 'None'}")
        print(f"Received text: {text}")
        # For now, just reload the page
        return redirect(url_for('upload'))
    
    return render_template('upload.html', 
                         title='Upload File and Content Display', 
                         heading='Upload File and Content Display')
=======
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
            return redirect(url_for('main.dashboard', user_id=current_user.id))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

      
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('main.register'))
        if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return redirect(url_for('main.register'))
            
            # Create new user

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()      
        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard', user_id=current_user.id))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard', user_id=user.id))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))



@main.route('/dashboard/<int:user_id>')
@login_required
def dashboard(user_id):
    if current_user.id != user_id:
        flash("Unauthorized access.")
        return redirect(url_for('main.dashboard', user_id=current_user.id))

    return render_template('dashboard.html', username=current_user.username, user_id