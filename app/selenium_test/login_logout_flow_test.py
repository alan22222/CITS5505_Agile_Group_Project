import os
import sys
import unittest
import threading
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def add_app_module():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    sys.path.append(project_root)

add_app_module()
from app import create_app, db  # noqa: E402

class TestAuthWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a Flask application with an in-memory database
        from config import TestConfig
        cls.app = create_app(config_class=TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        
        # Start Flask app in a separate thread
        def run_flask_app():
            cls.app.run(host='127.0.0.1', port=5001, use_reloader=False)
            
        cls.flask_thread = threading.Thread(target=run_flask_app)
        cls.flask_thread.daemon = True  # Set as a daemon thread so it automatically terminates when the main thread ends
        cls.flask_thread.start()
        print("Flask app started in the background")
        sleep(1)  # Give the Flask app some time to start

        # Configure Selenium
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Explicitly specify Chrome path
        
        # Use Service object to configure the driver
        service = Service(executable_path='/opt/homebrew/bin/chromedriver')
        cls.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)  # Increase implicit wait time

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        # Shutdown Flask app
        import requests
        try:
            requests.get('http://127.0.0.1:5001/shutdown', timeout=0.1)
        except requests.exceptions.RequestException:
            pass
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_full_auth_workflow(self):
        driver = self.driver
        test_username = "IamTestBot1"
        test_password = "BotPassword"
        test_email = "TestBot1@bot.com"

        # Step 1: Visit the homepage
        driver.get("http://127.0.0.1:5001")
        
        # Steps 2-5: Perform registration
        self._register_user(test_username, test_password, test_email)
        
        # Step 6: Verify registration success
        self._verify_registration_success()

        # Steps 7-8: Log in with the new account
        self._login_user(test_username, test_password)
        
        # Step 9: Verify login success
        self._verify_login_success()

        # Step 10: Test all links on the dashboard
        self._test_dashboard_links()

        # Steps 11-12: Perform logout and verify
        self._logout_and_verify()

    def _register_user(self, username, password, email):
        try:
            register_btn = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Register"))
            )
            register_btn.click()
        except Exception as e:
            self.fail(f"Failed to click the register button: {str(e)}")

        # Fill out the registration form
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = self.driver.find_element(By.NAME, "password")
        email_field = self.driver.find_element(By.NAME, "email")

        username_field.send_keys(username)
        password_field.send_keys(password)
        email_field.send_keys(email)

        # Submit the form
        submit_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Register')]"))
        )
        submit_btn.click()

    def _verify_registration_success(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/login"))
            flash_msg = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert"))
            ).text
            self.assertIn("Registration successful", flash_msg)
        except Exception as e:
            self.fail(f"Registration verification failed: {str(e)}")

    def _login_user(self, username, password):
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)

            submit_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]"))
            )
            submit_btn.click()
        except Exception as e:
            self.fail(f"Login process failed: {str(e)}")

    def _verify_login_success(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/dashboard"))
            welcome_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".welcome-header h2"))
            ).text
            self.assertIn("IamTestBot1", welcome_text)
        except Exception as e:
            self.fail(f"Login verification failed: {str(e)}")

    def _test_dashboard_links(self):
        try:
            test_links = [
                # Adjust validation element locators based on actual page structure
                ("Upload Data", "/upload", (".container form", "Upload Form")),
                ("Analyze", "/results", (".container .row", "Analysis Results Area")),
                ("Shares", "/shared_with_me", (".container", "Shared Files Page"))
            ]

            for link_text, expected_path, (element_locator, element_desc) in test_links:
                print(f"Testing link: {link_text}")
                try:
                    # Use a more stable locator strategy
                    link = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, 
                            f"//a[contains(@class, 'action-button')]//span[@class='action-text' and normalize-space()='{link_text}']/ancestor::a")
                        )
                    )
                    
                    # Add debug information
                    print(f"Element located successfully, position: {link.location}")
                    
                    # Use click with scroll and hover
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    ActionChains(self.driver)\
                        .move_to_element(link)\
                        .pause(1)\
                        .click()\
                        .perform()
                        
                    # Step-by-step waiting strategy
                    # 1. Wait for URL change first
                    WebDriverWait(self.driver, 20).until(
                        EC.url_contains(expected_path)
                    )
                    print(f"Successfully navigated to: {self.driver.current_url}")
                    
                    # 2. Then wait for the target element to be visible
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, element_locator))
                    )
                    print(f"Target element {element_desc} loaded successfully")
                    
                    # Enhanced back operation validation
                    self.driver.back()
                    # Wait for URL change first
                    WebDriverWait(self.driver, 20).until(
                        EC.url_matches(r".*/dashboard/?.*")
                    )
                    # Then wait for the element to be visible
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".stats-container"))
                    )
                    print("Successfully returned to dashboard")
                    sleep(1)  # Ensure DOM stability
                    
                except Exception as e:
                    current_html = self.driver.page_source[:1000]
                    print(f"Current page HTML snippet:\n{current_html}")
                    self.driver.save_screenshot(f"{link_text.replace(' ', '_')}_error.png")
                    self.fail(f"Link {link_text} test failed: {str(e)}\nCurrent URL: {self.driver.current_url}")

        except Exception as e:
            self.fail(f"Dashboard link test failed: {str(e)}")

    def _logout_and_verify(self):
        try:
            logout_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
            )
            logout_btn.click()
            
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/"))
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Login"))
            )
            self.assertTrue(login_btn.is_displayed())
        except Exception as e:
            self.fail(f"Logout process failed: {str(e)}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
