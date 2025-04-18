from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy credentials for demonstration
USERNAME = "admin"
PASSWORD = "password"

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == USERNAME and password == PASSWORD:
        return "Login successful!"
    else:
        return "Invalid credentials. Please try again."

if __name__ == '__main__':
    app.run(debug=True)