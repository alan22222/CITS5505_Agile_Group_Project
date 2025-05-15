import os
import sys
import time
import unittest
import multiprocessing
 
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 👇 NEW: Needed to load the test config
from app import create_app, db  # Create Flask app from app package
from config import TestConfig  # Import TestConfig from config.py
# from werkzeug.security import generate_password_hash

# 👇 NEW: Define a top-level function to launch Flask in a subprocess
def run_test_server():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        # from werkzeug.security import generate_password_hash
        db.create_all()  # 🔥 This creates all tables in the test DB
    app.run(port=5000, debug=False, use_reloader=False)  # Run Flask on port 5000

 
class E2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 1. Create the Flask app using the test config
        cls.app = create_app(config_class=TestConfig)

        # 2. Create the test database schema
        with cls.app.app_context():
            from app.models import User
            from werkzeug.security import generate_password_hash
            db.create_all()

            # Add a test user if not already present
            existing_user = User.query.filter_by(username="user1").first()
            if not existing_user:
                user = User(
                    username="user1",
                    email="u1@example.com",
                    password=generate_password_hash("Password123", 
                                                    method='pbkdf2:sha256',
                                                    salt_length=8)
                )
                db.session.add(user)
                db.session.commit()
                print("✅ User 'user1' created in test database.")
                print(f"Test user password hash: {user.password}")
            else:
                print("✅ User 'user1' already exists.")

        # 3. Start the Flask test server in a separate process
        cls.server_process = multiprocessing.Process(target=run_test_server)
        cls.server_process.start()
 
        # Make sure launching successfully
        time.sleep(5)
 
        # 4. Launch Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--incognito")  # Run in Incognito mode to avoid session retention
        chrome_options.add_argument("--disable-web-security")
        # For testing only! still not work for the login
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)
        cls.base_url = 'http://127.0.0.1:5000'  # Localhost URL for Flask app
 
    @classmethod
    def tearDownClass(cls):
        # Close the browser
        cls.driver.quit()
        # Kill Flask session
        cls.server_process.terminate()
        cls.server_process.join()
        # Drop the database
        with cls.app.app_context():
            from app import db
            db.drop_all()
 
    def test_register(self):
        # Test the registration process
        self.driver.get(f"{self.base_url}/register")
        
        print(f"Current URL: {self.driver.current_url}")

        # Print elements on the page
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print("\n--- Input Fields Detected ---")
        for i, elem in enumerate(inputs, 1):
            print(f"{i}. tag: <{elem.tag_name}> id: {elem.get_attribute('id')} name: {elem.get_attribute('name')} type: {elem.get_attribute('type')}")
        # Print the form on the page
        forms = self.driver.find_elements(By.TAG_NAME, "form")
        print("\n--- Forms Detected ---")
        for i, form in enumerate(forms, 1):
            print(f"{i}. form method: {form.get_attribute('method')} action: {form.get_attribute('action')}")

        # Fill out the registration form
        self.driver.find_element(By.ID, "username").send_keys("user2") 
        self.driver.find_element(By.ID, "email").send_keys("u2@example.com") 
        self.driver.find_element(By.ID, "password").send_keys("Password123") 
        print(f"Current URL after reg: {self.driver.current_url}")
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(0.5)
        print(f"Current URL after submit: {self.driver.current_url}")
        # Assert that the registration was successful (redirected to login)
        self.assertIn("/login", self.driver.current_url)

    
    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        self.driver.get(f"{self.base_url}/login")
        
        # Fill out the login form with invalid credentials
        self.driver.find_element(By.ID, "username").send_keys("invalid_user") # not exist user
        self.driver.find_element(By.ID, "password").send_keys("wrong_password")
        
        # Submit the form
        self.driver.find_element(By.TAG_NAME, "form").submit()
        time.sleep(0.5)
        
        # Assert that the user is redirected back to /login
        self.assertIn("/login", self.driver.current_url)

    def test_login(self):
        # Manually add the user if not already there
        with self.app.app_context():
            from app.models import User
            user = User.query.filter_by(username="user1").first()
            if user:
                print(f"✅ Retrieved user: {user.username}, ID: {user.id}, Password Hash: {user.password}")
            else:
                print("❌ User 'user1' not found in the database.")
                self.fail("Test user 'user1' was not found in the database.")
            expected_url_part = f"/dashboard/{user.id}"

        # Test the login process with valid credentials
        self.driver.get(f"{self.base_url}/login")

        # Print elements on the page
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        print("\n--- Input Fields Detected ---")
        for i, elem in enumerate(inputs, 1):
            print(f"{i}. tag: <{elem.tag_name}> id: {elem.get_attribute('id')} name: {elem.get_attribute('name')} type: {elem.get_attribute('type')}")

        # Fill out the login form
        self.driver.find_element(By.ID, "username").send_keys("user1")
        self.driver.find_element(By.ID, "password").send_keys("Password123")
        self.driver.find_element(By.TAG_NAME, "form").submit()

        # Print the current URL after form submission
        print(f"URL after login submit: {self.driver.current_url}")

        # Wait for the page to redirect to /dashboard/{user_id} after login
        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains(f"/dashboard/{user.id}")
            )
            print(f"URL after redirection: {self.driver.current_url}")
            self.assertIn(f"/dashboard/{user.id}", self.driver.current_url)
        except Exception as e:
            print(f"Login failed or redirection did not occur: {e}")
            self.fail("Login test failed due to redirection issue.")

if __name__ == "__main__":
    unittest.main()