import unittest
import time
import random
import string
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os

from run import create_app

LOCAL_URL = "http://127.0.0.1:5000"

app = None

def run_flask():
    global app
    app = create_app()
    app.run(port=5000)

class EndToEndTest(unittest.TestCase):
    @classmethod

    #randomly generate testuser and csv files
    def setUpClass(cls):
        cls.username = "testuser_" + ''.join(random.choices(string.ascii_lowercase, k=5))
        cls.password = "TestPass123"
        cls.email = cls.username + "@example.com"

        cls.csv_path = os.path.abspath("test_upload.csv")
        with open(cls.csv_path, "w") as f:
            f.write("Name,Age,Score\n")
            for i in range(20):
                f.write(f"User{i},{20+i},{80+i%10}\n")

        cls.server_thread = multiprocessing.Process(target=run_flask)
        cls.server_thread.start()
        time.sleep(3)

        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.server_thread.terminate()
        cls.server_thread.join()
        if os.path.exists(cls.csv_path):
            os.remove(cls.csv_path)
          
    #register test
    def test_1_register(self):
        self.driver.get(f"{LOCAL_URL}/register")
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        register_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", register_btn)
        WebDriverWait(self.driver, 10).until(EC.url_contains("login"))
      
    #login test
    def test_2_login(self):
        self.driver.get(f"{LOCAL_URL}/login")
        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", login_btn)
        WebDriverWait(self.driver, 10).until(lambda d: "dashboard" in d.current_url or "upload" in d.current_url)

    #upload test
    def test_3_upload(self):
        self.driver.get(f"{LOCAL_URL}/upload")
        if "/login" in self.driver.current_url:
            self.test_2_login()
            self.driver.get(f"{LOCAL_URL}/upload")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "fileUpload")))
        self.driver.find_element(By.ID, "fileUpload").send_keys(self.csv_path)
        self.driver.find_element(By.ID, "uploadName").send_keys("Test Upload")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(self.driver, 10).until(EC.url_contains("select_model"))

    #select model test
    def test_4_select_model(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "file_select")))
        Select(self.driver.find_element(By.NAME, "file_select")).select_by_index(1)
        Select(self.driver.find_element(By.NAME, "model_type")).select_by_visible_text("Linear Regression")
        Select(self.driver.find_element(By.NAME, "precision_mode")).select_by_visible_text("Fast")
        self.driver.find_element(By.NAME, "target_index").send_keys("1")

        checkbox = self.driver.find_element(By.NAME, "has_header")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", checkbox)

        go_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", go_btn)
        WebDriverWait(self.driver, 10).until(EC.url_contains("results"))
        time.sleep(5)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    unittest.main()
