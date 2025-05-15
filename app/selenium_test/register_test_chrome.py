import os
import time
import threading
import unittest
import os
import sys
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
from flask_login import LoginManager
from app.models import User, db 

# Create a memory based database with sqlite3
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False  # Ban CSRF
app.config['TESTING'] = True

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Loading user call back
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register user blue print
from app.routes import main
app.register_blueprint(main)

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
            db.create_all()

    def tearDown(self):
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
