import json
import os
from datetime import datetime

import pandas as pd
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from app import db
from app.forms import SelectModelForm
from app.models import ModelRun, SharedResult, UploadedData, User
from app.static.ml_model.DataWashing import DataWashing
from app.static.ml_model.GPT_result_analysation import (
    kmeans_assistant, linear_regression_assistant, svm_classifier_assistant)
from app.static.ml_model.GPTassistant import GPT_column_suggestion
from app.static.ml_model.K_means import kmeans_function
from app.static.ml_model.LinearRegression import LinearRegressionTraining
from app.static.ml_model.SVM_classifier import SVMClassifier

main = Blueprint('main', __name__)#flask blueprint definied and stored

@main.route('/')
def index():
    # login to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard', user_id=current_user.id))
    # logout to landing page
    return render_template('landing.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    #redirect authenticated user to the dahsboard
    if current_user.is_authenticated:
            return redirect(url_for('main.dashboard', user_id=current_user.id))
    #handle the user submission 
    if request.method == 'POST':
        username = request.form.get('username')#username from iser
        email = request.form.get('email')#email form the user
        password = request.form.get('password')#get the password formuser

      #check if the isername already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('main.register'))
            #check if the email already exists
        if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return redirect(url_for('main.register'))
            
            
        # Create new user
        hashed_pw = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )#hashed  password for security
        new_user = User(username=username, email=email, password=hashed_pw)#new user instance is created
        db.session.add(new_user)#add new user to db
        db.session.commit()      #save the user in  database
        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))#redirected to login page 

    return render_template('register.html')#request for registration is displayed

# Route for handling login page and authentication
@main.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard', user_id=current_user.id))
    
    # Handle form submission (POST request)
    if request.method == 'POST':
        username = request.form['username']# Get username from form
        password = request.form['password']# Get password from form

        # Query database for user with the given username
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            print(f"✅ Login success for {username}")
            login_user(user)
            return redirect(url_for('main.dashboard', user_id=user.id))# Redirect to dashboard
        else:
            print(f"❌ Login failed for {username}")
            flash("Invalid credentials.")# Flash error message to user
            return redirect(url_for('main.login'))# Reload login page
    # For GET request, render the login page
    return render_template('login.html')

# Route for handling user logout
@main.route('/logout')
@login_required # Ensure the user is logged in before allowing logout
def logout():
    logout_user() # Log the user out (clears session)
    return redirect(url_for('main.index'))


# Routes for viewing the user dashboard, with or without explicit user_id in the URL
@main.route('/dashboard')
@main.route('/dashboard/<int:user_id>')
@login_required
def dashboard(user_id=None):
    # Prevent unauthorized access to another user's dashboard
    if user_id and user_id != current_user.id:
        flash("Unauthorized access.")
        return redirect(url_for('main.dashboard'))
    # Fetch datasets uploaded by the current user, ordered by upload date (most recent first)
    datasets = UploadedData.query.filter_by(user_id=user_id).order_by(UploadedData.upload_date.desc()).all()
    datasets_count = len(datasets) 
    # Fetch ML model run history for the current user, ordered by most recent
    dataset_modelrun = ModelRun.query.filter_by(user_id=user_id).order_by(ModelRun.created_at.desc()).all()
    model_count = len(dataset_modelrun)
    # Fetch results shared with the current user, ordered by most recent
    received_result = SharedResult.query.filter_by(receiver_id=current_user.id).order_by(SharedResult.shared_at.desc()).all()
    share_result_count = len(received_result)
    # Render the dashboard template with all relevant user-specific data
    return render_template('dashboard.html', username=current_user.username, user_id=current_user.id, datasets=datasets,
                           datasets_count=datasets_count, model_count=model_count, share_result_count=share_result_count)

# Route to handle CSV file upload and automatic target column suggestion using GPT
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

        # Validate file input
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('data', 'uploads', str(current_user.id))
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        df = pd.read_csv(filepath)#read csv

        # Slice the dataset and prepare JSON
        data_slice = df.head(10).values.tolist()  # Only send top 10 rows to GPT
        gpt_input = {
            "data": data_slice,
            "label_column": -1  # Dummy label column, GPT will analyze all
        }

        # Use your GPT_column_suggestion function
        suggested_target_col = GPT_column_suggestion(json.dumps(gpt_input))


        # Get file stats
        file_stats = os.stat(filepath)
        file_size = file_stats.st_size  # in bytes
        upload_date = datetime.fromtimestamp(file_stats.st_ctime)

        # Save upload info to database
        uploaded_data = UploadedData(
            filename=filename,
            file_path=filepath,
            file_size=file_size,
            user_id=current_user.id,
            upload_date=datetime.now()
        )
        db.session.add(uploaded_data)
        db.session.commit()
        flash(f" The {filename} is successfully uploaded.", "success")
        flash(f"The suggested target index from AI is {suggested_target_col}", "info")#gpt suggeste column number/string
        return redirect(url_for('main.select_model', data_id=uploaded_data.id ,suggested_col=suggested_target_col, column_names=list(df.columns), filename=filename ))

    return render_template(
        'upload.html',
        title='Upload File and Content Display',
        heading='Upload File and Content Display'
    )

# Route to handle deletion of an uploaded file
@main.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    # Fetch the dataset by ID or return 404 if not found
    dataset = UploadedData.query.get_or_404(file_id)

    # Check if the current user owns the file
    if dataset.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('main.dashboard', user_id=current_user.id))
    # Delete the file from the file system if it exists
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    # Remove the dataset record from the database
    db.session.delete(dataset)
    db.session.commit()
    flash(f"File '{dataset.filename}' has been deleted.", "success")
    return redirect(url_for('main.dashboard', user_id=current_user.id))

# Route to handle model selection and execution
@main.route('/select_model', methods=['GET', 'POST'])
@login_required
def select_model():
    form = SelectModelForm() # Initialize form for model selection
    # get user id
    user_id = current_user.id
    form.user_id.data = current_user.id # Pre-fill form with current user ID

    upload_path = os.path.join('data', 'uploads', str(user_id))#fl stored in the data/uploads/<user_id>/csv we ar joining t
    # Try to list all CSV files uploaded by the user
    try:
        file_list = os.listdir(upload_path)
        file_list = [f for f in file_list if f.endswith('.csv')] #csv only check
    except FileNotFoundError:
        file_list = []
    # Handle form submission
    if form.validate_on_submit():
        # read the parameters
        user_id        = form.user_id.data
        model_type     = form.model_type.data
        precision_mode = form.precision_mode.data
        target_index   = form.target_index.data
        has_header     = form.has_header.data
        selected_file = request.form.get('file_select')
        print("user_id =", user_id)
        print("selected_file =", selected_file)

        # Construct full file path and load dataset
        filepath = os.path.join(upload_path, selected_file)
        raw_df = pd.read_csv(filepath, header=0 if has_header else None)
        cleaned_df = DataWashing(raw_df) # Clean the data before training

        # Execute the selected model based on user's choice

        if model_type == 'SVM':
            result, success = SVMClassifier(cleaned_df, target_index, precision_mode)
        elif model_type == 'linear_regression':
            result, success = LinearRegressionTraining(cleaned_df, target_index, precision_mode)
        elif model_type == 'KMeans':
            result, success = kmeans_function(cleaned_df, precision_mode)
        else:
            result, success = {'error': 'Unsupported model type'}, False

        if success:
            # Save result to DB (optional)
            model_run = ModelRun(
                user_id=user_id,
                filename=selected_file,
                model_type=model_type,
                precision_mode=precision_mode,
                target_index=target_index,
                has_header=has_header,
                graph_path=result.get('plot_path'),
                
                result_json=json.dumps(result),
                created_at=datetime.now()
            )
            db.session.add(model_run)
            db.session.commit()
            flash("Model execution success: " + str(result), "success")
            return redirect(url_for('main.results'))

        else:
            flash("Model execution failed: " + str(result), "danger")

        return redirect(url_for(
            'main.dashboard',
            filename=selected_file,
            user_id=user_id,
            model_type=model_type,
            precision_mode=precision_mode,
            target_index=target_index,
            has_header=int(has_header)
        ))
    # If GET request or form not valid, show model selection page
    return render_template('select_model.html',
                           heading='Select Model Parameters', 
                           form=form,
                           file_list=file_list)

# Route to display the user's past model run results
@main.route('/results', methods=['GET'])
@login_required
def results():
    user_id = current_user.id
    # Query all model runs by the user, ordered from most recent to oldest
    results = ModelRun.query.filter_by(user_id=user_id).order_by(ModelRun.created_at.desc()).all()
    # Render the results page with the retrieved model run data
    return render_template('results.html',
                           heading='Your Model Insights',
                           results=results)

# Route to handle sharing a model run result with another user
@main.route('/share_result/<int:run_id>', methods=['POST'])
@login_required
def share_result(run_id):
    # Get the recipient's username from the form
    recipient_username = request.form.get('recipient_username')
    # Look up the recipient user by username
    recipient = User.query.filter_by(username=recipient_username).first()

    if not recipient:
        flash("User not found.", "danger")
        return redirect(url_for('main.dashboard'))
    # Prevent user from sharing with themselves
    if recipient.id == current_user.id:
        flash("You cannot share a result with yourself.", "warning")
        return redirect(url_for('main.dashboard', user_id=current_user.id))

    # Retrieve the original model run or 404 if not found

    original = ModelRun.query.get_or_404(run_id)
    if original.user_id != current_user.id:
        flash("Unauthorized share attempt.", "danger")
        return redirect(url_for('main.dashboard'))

    # Save shared result as a reference
    shared = SharedResult(
        sender_id=current_user.id,
        receiver_id=recipient.id,
        modelrun_id=original.id,
        result_snapshot=original.result_json,
        shared_at=datetime.now()
    )
    # Commit the shared result to the database
    db.session.add(shared)
    db.session.commit()
    flash(f"Result shared with {recipient_username}.", "success")
    return redirect(url_for('main.dashboard', user_id=current_user.id))

# Route to display detailed results of a specific model run
@main.route('/view_result/<int:run_id>')
@login_required
def view_result(run_id):
    # Fetch the model run by ID or return 404 if not found
    run = ModelRun.query.get_or_404(run_id)
    if run.user_id != current_user.id:
        flash('The result is as below.')

    # Optionally parse JSON
    import json
    metrics = {}
    if run.result_json:
        try:
            metrics = json.loads(run.result_json)
        except:
            pass
     # Use model-specific GPT assistant to interpret the results
    if run.model_type=='linear_regression':
        gpr_answer=linear_regression_assistant(run.result_json)
        print(gpr_answer)
    elif run.model_type=='KMeans':
                gpr_answer=kmeans_assistant(run.result_json)
    elif run.model_type=='SVM':
        gpr_answer=svm_classifier_assistant(run.result_json)
    else:
        flash("model name not found")
        gpr_answer = "N/A"

    return render_template('view.html', run=run, metrics=metrics,gpr_answer=gpr_answer)

# Route to display results shared with the current use
@main.route('/shared_with_me')
@login_required
def shared_with_me():
    # Query all results where the current user is the receiver

    shared_items = SharedResult.query.filter_by(receiver_id=current_user.id).all()

    # Attach parsed JSON metrics to each shared result for easy display
    for item in shared_items:
        try:
            item.parsed_metrics = json.loads(item.result_snapshot)
        except:
            item.parsed_metrics = {}

    return render_template('shared_results.html',
                            heading='Shared with You',
                            shared_items=shared_items)
    
# Route to provide username suggestions for autocomplete (e.g., in result sharing)
@main.route('/username_autocomplete')
@login_required
def username_autocomplete():
    # Get the search query from the request parameters (default to empty string)
    query = request.args.get('q', '')
    # Search for usernames that partially match the query, case-insensitive
    # Exclude the current user from the results
    results = User.query.filter(User.username.ilike(f"%{query}%")).filter(User.id != current_user.id).limit(5).all()
    usernames = [user.username for user in results]
    return jsonify(usernames=usernames)
