import unittest
import time
import os
import sys
# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import db, create_app  # Import your Flask app and db
from app.models import User  # Import your User model
from werkzeug.security import generate_password_hash

class TestLoginRegister(unittest.TestCase):

    BASE_URL = "http://localhost:5000"  # Adjust if your app runs on a different port

    def setUp(self):
        # Set up the Chrome driver
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.get(self.BASE_URL)

        # Set up a test Flask app context
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create the database and tables (if they don't exist)
        db.create_all()

        # Create a test user in the database
        self.test_username = "testuser"
        self.test_email = "test@example.com"
        self.test_password = "password"
        hashed_password = generate_password_hash(self.test_password, method='pbkdf2:sha256')

        # Check if the user already exists
        existing_user = User.query.filter_by(username=self.test_username).first()
        if not existing_user:
            test_user = User(username=self.test_username, email=self.test_email, password=hashed_password)
            db.session.add(test_user)
            db.session.commit()

    def tearDown(self):
        self.driver.quit()

        # Clean up the database after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self, username, email, password):
        self.driver.get(f"{self.BASE_URL}/register")
        username_field = self.driver.find_element(By.ID, "username")
        email_field = self.driver.find_element(By.ID, "email")
        password_field = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']") # Find by xpath for register button

        username_field.send_keys(username)
        email_field.send_keys(email)
        password_field.send_keys(password)
        submit_button.click()

    def login_user(self, username, password):
         self.driver.get(f"{self.BASE_URL}/login")
         username_field = self.driver.find_element(By.ID, "username")
         password_field = self.driver.find_element(By.ID, "password")
         submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

         username_field.send_keys(username)
         password_field.send_keys(password)
         submit_button.click()

    def test_register_success(self):
        self.register_user("newuser123", "new@example.com", "newpassword")
        # Wait for a redirect or a success message
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/login")  # Assuming you're redirected to login on success
        )
        self.assertIn("/login", self.driver.current_url)

    def test_register_username_exists(self):
        # Try to register the same user again
        self.register_user(self.test_username, "test2@example.com", "password2")

        # Wait for an alert
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertEqual("Username already exists!", alert.text)
        alert.accept()  # Close the alert

    def test_login_success(self):
        # Then log in
        self.login_user(self.test_username, self.test_password)
        # Verify successful login (e.g., by checking for a redirect to the dashboard)
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )
        self.assertIn("/dashboard", self.driver.current_url)

    def test_login_failure(self):
        self.login_user("wronguser", "wrongpassword")
        # Verify login failure (e.g., by checking for an error message)
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertEqual("Invalid credentials.", alert.text)
        alert.accept()

if __name__ == "__main__":
    unittest.main()
