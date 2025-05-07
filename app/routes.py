import os
from datetime import datetime

from app import db
from app.models import UploadedData, User
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app.forms import SelectModelForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # login to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard', user_id=current_user.id))
    # logout to landing page
    return render_template('landing.html')


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
            session["user_name"] = username
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



@main.route('/dashboard')
@main.route('/dashboard/<int:user_id>')
@login_required
def dashboard(user_id=None):
    if user_id and user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for('main.dashboard'))
    
    datasets = UploadedData.query.filter_by(user_id=user_id).order_by(UploadedData.upload_date.desc()).all()
    datasets_count = len(datasets) 
    return render_template('dashboard.html', username=current_user.username, user_id=current_user.id, datasets=datasets,datasets_count=datasets_count)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Get file and form data
        file = request.files.get('file')
        text = request.form.get('text')
        upload_name = request.form.get('upload_name')

        if not file:
            flash("No file selected.", "danger")
            return redirect(url_for('main.upload'))

        # Save file securely
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('data', 'uploads', str(current_user.id))
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Get file stats
        file_stats = os.stat(filepath)
        file_size = file_stats.st_size  # in bytes
        created_at = datetime.fromtimestamp(file_stats.st_ctime)

        # Validate whether the uploaded file is a legal csv file
        flag = FileValidation(filepath)
        if flag == False:
            flash("Invalid file format. Please upload a CSV file.", "danger")
            return redirect(url_for('main.upload'))
        clean_data = DataWashing(filepath)
        sample_data = clean_data.head(3) # sample data is used for GPT suggestion rather than training. So just leav it alone for now

        # Save upload info to database
        uploaded_data = UploadedData(
            filename=filename,
            file_path=filepath,
            file_size=file_size,
            created_at=created_at,
            user_id=current_user.id,
            upload_date=datetime.now()
        )
        db.session.add(uploaded_data)
        db.session.commit()
        current_result, process_flag, status_code= data_analysation(clean_data)
        print(current_result)
        print(process_flag)
        flash(f"Upload successful: {filename}", "success")
        return redirect(url_for('main.select_model', data_id=uploaded_data.id))

    return render_template(
        'upload.html',
        title='Upload File and Content Display',
        heading='Upload File and Content Display'
    )

@main.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    dataset = UploadedData.query.get_or_404(file_id)

    # Ensure user owns the file
    if dataset.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('main.dashboard'))

    # Delete file from filesystem if it exists
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)

    # Delete from database
    db.session.delete(dataset)
    db.session.commit()
    flash(f"File '{dataset.filename}' deleted.", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/select_model', methods=['GET', 'POST'])
@login_required
def select_model():
    form = SelectModelForm()
    # get user id
    form.user_id.data = current_user.id

    if form.validate_on_submit():
        # read the parameters
        user_id        = form.user_id.data
        model_type     = form.model_type.data
        precision_mode = form.precision_mode.data
        target_index   = form.target_index.data
        has_header     = form.has_header.data

        
        return redirect(url_for(
            'main.dashboard',
            user_id=user_id,
            model_type=model_type,
            precision_mode=precision_mode,
            target_index=target_index,
            has_header=int(has_header)
        ))

    return render_template('select_model.html', form=form)
