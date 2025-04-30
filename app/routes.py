import os as os
from datetime import datetime

from flask import (Blueprint, flash, json, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app import db
from app.models import ModelRun, UploadedData, User

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
    # Only allow access to own dashboard
    if current_user.id != user_id:
        flash("Unauthorized access.")
        return redirect(url_for('main.login'))

    # Fetch only current user's model runs
    my_results = ModelRun.query.filter_by(user_id=user_id).order_by(ModelRun.created_at.desc()).all()

    # Fetch shared results for this user

    return render_template('dashboard.html',
                           results=my_results,
                           username=current_user.username, user_id=user_id)




@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # 1. Get the uploaded file
        file = request.files['csv_file']
        filename = secure_filename(file.filename)
        filepath = os.path.join('data', filename)
        file.save(filepath)
        
        # 2. Get form fields
        model_type = request.form['model_type']
        speed_mode = request.form['speed_mode']
        target_index = int(request.form['target_column'])
        has_header = 'has_header' in request.form

        # 3. Read CSV
        import pandas as pd
        df = pd.read_csv(filepath, header=0 if has_header else None)

        # 4. Run the selected model
        result_metrics, plot_filename = run_model(df, model_type, target_index, speed_mode)
        new_data=UploadedData(
            user_id=current_user.id,
            filename=filename ,
            graph_path=plot_filename,
            upload_date=datetime.now()
        )   
        # 5. Save the result to database
        new_run = ModelRun(
            user_id=current_user.id,
            model_type=model_type,
            precision_mode=speed_mode,
            target_index=target_index,
            has_header=has_header,
            result_json=json.dumps(result_metrics),
            graph_path=plot_filename
        )
        
        db.session.add(new_run)
        db.session.add(new_data)
        db.session.commit()

        flash("Analysis complete! Results added to your dashboard.")
        return redirect(url_for('main.dashboard', user_id=current_user.id))

    return render_template('upload.html')
def run_model(df, model_type, target_index, speed_mode):
    import uuid

    import matplotlib.pyplot as plt
    from sklearn import svm
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, r2_score

    X = df.drop(df.columns[target_index], axis=1)
    y = df.iloc[:, target_index]

    if model_type == 'linear_regression':
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)

        # Plot
        fig, ax = plt.subplots()
        ax.scatter(y, y_pred)
        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")
        ax.set_title("Linear Regression: Actual vs Predicted")

        # Save graph
        plot_name = f"{uuid.uuid4().hex}.png"
        plot_path = os.path.join('app', 'static', 'plots', plot_name)
        fig.savefig(plot_path)
        plt.close(fig)

        return {
            "MAE": float(mean_absolute_error(y, y_pred)),
            "R2 Score": float(r2_score(y, y_pred))
        }, plot_name

    elif model_type == 'kmeans':
        model = KMeans(n_clusters=3 if speed_mode == "fast" else 5)
        model.fit(X)
        labels = model.labels_

        fig, ax = plt.subplots()
        ax.scatter(X.iloc[:, 0], X.iloc[:, 1], c=labels)
        ax.set_title("K-Means Clustering")

        plot_name = f"{uuid.uuid4().hex}.png"
        plot_path = os.path.join('app', 'static', 'plots', plot_name)
        fig.savefig(plot_path)
        plt.close(fig)

        return {
            "Inertia": float(model.inertia_),
            "Clusters": len(set(labels))
        }, plot_name

    # Add more models like SVM as needed
