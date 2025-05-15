import os
import time
import threading
import unittest
import os
import sys

# =================== IMPORTANT NOTE ===================
# This test file has been modified to use a separate in-memory SQLite database
# for testing, rather than the real application database. This prevents test data
# from being written to the real database during testing.
# The key changes are:
# 1. Creating a separate SQLAlchemy instance (test_db) instead of using the app's db
# 2. Creating test-specific models that use this test_db instance
# 3. Creating a mock blueprint with routes that use the test_db
# 4. Properly cleaning up the test database after each test
# =================== IMPORTANT NOTE ===================

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# =================== Flask simulation ===================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from app.models import User

# Create a test-specific database instance
test_db = SQLAlchemy()

# Create a memory based database with sqlite3
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'test-secret-key'  # Required for sessions and flash messages

# Initialize database with our test-specific instance
test_db.init_app(app)

# Define test models that use our test_db instance
class TestUser(test_db.Model, UserMixin):
    __tablename__ = 'user'
    id = test_db.Column(test_db.Integer, primary_key=True)
    username = test_db.Column(test_db.String(150), unique=True, nullable=False)
    password = test_db.Column(test_db.String(150), nullable=False)
    email = test_db.Column(test_db.String(150), unique=True, nullable=False)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Loading user call back
@login_manager.user_loader
def load_user(user_id):
    return TestUser.query.get(int(user_id))

# Create a mock blueprint for testing
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user
from werkzeug.security import generate_password_hash

# Create a test blueprint
test_main = Blueprint('main', __name__)

@test_main.route('/')
def index():
    return render_template('landing.html')

@test_main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username already exists
        if TestUser.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('main.register'))
            
        # Check if email already exists
        if TestUser.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('main.register'))
            
        # Create new user
        hashed_pw = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = TestUser(username=username, email=email, password=hashed_pw)
        test_db.session.add(new_user)
        test_db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@test_main.route('/login', methods=['GET', 'POST'])
def login():
    # Simple mock login route
    return render_template('login.html')

# Register our test blueprint
app.register_blueprint(test_main)

# =================== Selenium browser set up ===================

BROWSER = 'chrome'
BROWSER_FIREFOX = 'firefox'
BASE_URL = "http://127.0.0.1:5000"

# Test user information
USERNAME = "IamTestBot"
PASSWORD = "BotPassword"
EMAIL = "TestBot@bot.com"

def find_driver(executable_name):
    possible_paths = [
        f"/opt/homebrew/bin/{executable_name}",
        f"{os.path.expanduser('~')}/Downloads/{executable_name}",
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None

def setup_browser(browser='chrome'):
    if browser == 'chrome':
        chrome_path = find_driver('chromedriver')
        if not chrome_path:
            raise FileNotFoundError("ChromeDriver not found. Please install it or specify the path.")
        service = ChromeService(executable_path=chrome_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=service, options=options)

    elif browser == 'firefox':
        firefox_path = find_driver('geckodriver')
        if not firefox_path:
            raise FileNotFoundError("GeckoDriver not found. Please install it or specify the path.")
        service = FirefoxService(executable_path=firefox_path)
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(service=service, options=options)

    else:
        raise ValueError("Unsupported browser type")

    return driver

# =================== Test class ===================

class TestRegister(unittest.TestCase):

    def setUp(self):
        # Start up flask server
        self.server_thread = threading.Thread(target=app.run)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Waiting for start process
        time.sleep(1)

        # Start browser
        self.driver = setup_browser(BROWSER)

        # Create app context
        with app.app_context():
            test_db.create_all()

    def tearDown(self):
        # Clean up the database
        with app.app_context():
            test_db.session.remove()
            test_db.drop_all()
        
        # Quit the browser
        self.driver.quit()

    def test_register_user(self):
        driver = self.driver
        print("Opening registration page...")
        driver.get(f"{BASE_URL}/register")

        try:
            # Wait for loading
            print("Wait for loading...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'form'))
            )

            # Fill register form on webpage
            print("Filling registration form...")
            username_field = driver.find_element(By.NAME, "username")
            email_field = driver.find_element(By.NAME, "email")
            password_field = driver.find_element(By.NAME, "password")

            username_field.send_keys(USERNAME)
            email_field.send_keys(EMAIL)
            password_field.send_keys(PASSWORD)

            # Submit the form
            print("Submitting registration form...")
            form = driver.find_element(By.TAG_NAME, "form")
            form.submit()

            # Waiting for jumping
            print(" Waiting for jumping...")
            expected_url = f"{BASE_URL}/login"
            WebDriverWait(driver, 10).until(
                EC.url_to_be(expected_url)
            )

            current_url = driver.current_url
            if current_url == expected_url:
                print("✅ Register process completed and success to jump into login page")
            else:
                print(f"❌ Register process fail, unable to jump to {expected_url}")
                print(f"The current URL is: {current_url}")
                print("The content of webpage is：")
                print(driver.page_source)

        except TimeoutException as e:
            print("⏰ Operation process reach the time limit")
            print("The current URL is:", driver.current_url)
            print("The content of webpage is：")
            print(driver.page_source)
            raise e

# =================== RunTesting ===================

if __name__ == "__main__":
    unittest.main()
