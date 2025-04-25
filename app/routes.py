# from app import app
# from flask import render_template, request # add this time


# @app.route('/')
# def index():
#     return "Hello World"

# # below add this time
# @app.route('/')
# def index():
#     return render_template("login.html")  # change this if you prefer another default

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     return render_template("login.html")

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         # Handle file upload here if needed
#         pass
#     return render_template("upload.html")



# # from app import app

# # @app.route('/')
# # def index():
# #     # return "Hello World"
# #     return render_template('login.html')



# from flask import render_template, redirect, url_for
# from . import app

# @app.route('/')
# def home():
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET'])
# def login():
#     return render_template('login.html')

# @app.route('/upload', methods=['GET'])
# def upload():
#     return render_template('upload.html')

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