# app/selenium_test/sharing_test.py
import os
import sys
import sqlite3
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

# 截图函数
def take_screenshot(driver, name="error"):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"截图已保存为: {filename}")

# 将项目根目录加入 Python 路径
def add_app_module():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    sys.path.append(project_root)

add_app_module()

# 初始化内存数据库的 SQL 脚本
INIT_SQL = """
CREATE TABLE user (
    id INTEGER NOT NULL, 
    username VARCHAR(150) NOT NULL, 
    password VARCHAR(150) NOT NULL, 
    email VARCHAR(150) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (username), 
    UNIQUE (email)
);

CREATE TABLE model_run (
    id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    filename VARCHAR(255) NOT NULL, 
    model_type VARCHAR(50) NOT NULL, 
    precision_mode VARCHAR(50) NOT NULL, 
    target_index INTEGER NOT NULL, 
    has_header BOOLEAN, 
    created_at DATETIME NOT NULL, 
    result_json TEXT, 
    graph_path VARCHAR(255), 
    PRIMARY KEY (id)
);

CREATE TABLE uploaded_data (
    id INTEGER NOT NULL, 
    filename VARCHAR(120) NOT NULL, 
    file_path VARCHAR(200) NOT NULL, 
    file_size INTEGER NOT NULL, 
    upload_date DATETIME, 
    user_id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id)
);

CREATE TABLE shared_result (
    id INTEGER NOT NULL, 
    sender_id INTEGER NOT NULL, 
    receiver_id INTEGER NOT NULL, 
    modelrun_id INTEGER NOT NULL, 
    shared_at DATETIME, 
    result_snapshot TEXT NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(sender_id) REFERENCES user (id), 
    FOREIGN KEY(receiver_id) REFERENCES user (id), 
    FOREIGN KEY(modelrun_id) REFERENCES model_run (id)
);

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INSERT INTO user (id, username, password, email) VALUES
(1, 'test', 'scrypt:32768:8:1$hLV9uFa2j1AzfnmF$aa627facae02c3b125ccf0a2a4b716b089e9738efb1d9ccb93091cfa08e1fe51ff484742bdd4275736740091cf3fbbcd017ea89748d01bc3c209b60b2fd07487', 'testuser@gmail.com'),
(2, 'admin', 'scrypt:32768:8:1$3Sexhj6tZxm6nSwl$f250219b953f2227f6547ad613b0a5cfb0f86b598bd6d46c1130e1d0b018e55dfe7edfe99d56bc44822cab3389ad7431a4a1b9905b40cee857d137ec5d4ceee7', 'alanchacko42@gmail.com'),
(3, 'karen', 'scrypt:32768:8:1$T3zJssu0vbvSZgWn$65e12998fef50191cf5d12377d638a529df1adf197baf79a44aece418263126fd5d241dccea37841b3e2d0451fb9a4a6603158950266dea884b475d519fadfb1', 'karen@uwa.com.au');

INSERT INTO model_run (id, user_id, filename, model_type, precision_mode, target_index, has_header, created_at) VALUES
(1, 3, 'regression_data.csv', 'linear_regression', 'fast', 1, 1, '2024-05-01 10:00:00');

INSERT INTO shared_result (id, sender_id, receiver_id, modelrun_id, shared_at, result_snapshot) VALUES
(1, 3, 1, 1, '2024-05-01 11:00:00', '{"accuracy": 0.95, "mse": 0.12}');
"""

class TestSharingWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 初始化内存数据库
        cls.conn = sqlite3.connect(':memory:')
        cls.cursor = cls.conn.cursor()
        cls.cursor.executescript(INIT_SQL)
        cls.conn.commit()

        # 配置浏览器
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_service = webdriver.chrome.service.Service(
            '/opt/homebrew/bin/chromedriver')
        cls.driver = webdriver.Chrome(
            service=chrome_service, options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.driver.quit()

    def test_full_workflow(self):
        self._karen_workflow()
        self._test_user_verification()

    def _karen_workflow(self):
        driver = self.driver
        try:
            # Step 1: Karen登录
            driver.get("http://localhost:5000/login")
            driver.find_element(By.NAME, 'username').send_keys('karen')
            driver.find_element(By.NAME, 'password').send_keys('password')
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            self.assertNotIn("Invalid credentials", driver.page_source)

            # Step 2: 导航到上传页面
            upload_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.action-button.upload-btn')))
            upload_btn.click()
            self.assertIn('/upload', driver.current_url)

            # Step 3: 上传文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
            file_path = os.path.join(project_root, 'tests', 'regression_data.csv')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"测试文件不存在于: {file_path}")
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]')))
            file_input.send_keys(file_path)


            # 提交上传按钮
            upload_submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary'))
            )
            # Scroll into view using ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(upload_submit_button).perform()
            
            # ✅ 截图验证滚动是否成功
            take_screenshot(driver, "after_actionchains_scroll_to_upload_button")
            
            # ✅ 安全点击
            try:
                # Wait briefly for the element to be clickable after scroll/move.
                # The element reference 'upload_submit_button' is used directly.
                clickable_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(upload_submit_button) 
                )
                clickable_button.click()
            except Exception as e:
                print(f"Standard click failed after ActionChains scroll: {e}. Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", upload_submit_button)

            # Step 4: 等待并跳转到模型选择页面
            WebDriverWait(driver, 10).until(EC.url_contains('/select_model'))
            self.assertIn('/select_model', driver.current_url)

            # Step 5: 填写模型参数
            select_file = Select(WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'file_select'))))
            select_file.select_by_visible_text('regression_data.csv')

            select_model_type = Select(driver.find_element(By.ID, 'model_type'))
            select_model_type.select_by_visible_text('Linear Regression')

            select_precision = Select(driver.find_element(By.ID, 'precision_mode'))
            select_precision.select_by_visible_text('Fast')

            driver.find_element(By.ID, 'target_index').send_keys('1')

            # 提交模型配置
            model_submit_button_selector = (By.CSS_SELECTOR, '.btn.btn-primary') # Assuming this is the correct selector for this page
            
            # Ensure the button is present
            model_submit_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(model_submit_button_selector)
            )
            
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", model_submit_element)
            time.sleep(0.5) # Brief pause for smooth scroll

            # Wait for the element to be clickable after scrolling
            clickable_model_submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(model_submit_element)
            )
            
            take_screenshot(driver, "before_click_model_submit") # Debug screenshot

            try:
                # Using ActionChains for a more robust click
                actions = ActionChains(driver)
                actions.move_to_element(clickable_model_submit_button).click().perform()
                print("Clicked model submit button using ActionChains.")
            except Exception as e:
                print(f"ActionChains click failed for model submit button: {e}. Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", clickable_model_submit_button)
                print("Clicked model submit button using JavaScript.")

            # Step 6: 等待结果页面
            WebDriverWait(driver, 10).until(EC.url_contains('/results'))
            self.assertIn('/results', driver.current_url)

            result_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.col-md-5.mb-4')))
            self.assertGreaterEqual(len(result_cards), 1)

            # Step 7: 分享结果
            last_card_for_share = result_cards[-1]
            share_button_css_selector = '.btn.btn-info.btn-sm[data-bs-toggle="modal"]'
            
            # First, ensure the button is present within the card
            share_button_element = WebDriverWait(last_card_for_share, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, share_button_css_selector))
            )
            
            # Scroll the element into view
            # Using 'smooth' scrolling and ensuring it's centered.
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", share_button_element)
            time.sleep(0.5) # Brief pause for smooth scroll animation to settle

            # Now, wait for the *same element reference* to be clickable after scrolling
            clickable_share_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(share_button_element) 
            )
            driver.save_screenshot("before_click_share.png")  # 截图调试

            try:
                # Using ActionChains for a more robust click after scrolling
                actions = ActionChains(driver)
                actions.move_to_element(clickable_share_button).click().perform()
                print("Clicked share button using ActionChains.")
            except Exception as e:
                print(f"ActionChains click failed for share button: {e}. Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", clickable_share_button)
                print("Clicked share button using JavaScript.")

            # Step 8: 填写分享 Modal 并提交
            time.sleep(1) # Allow a moment for modal to start appearing

            modal_selector = (By.CSS_SELECTOR, 'div.modal.show') # More specific for Bootstrap 5
            modal = WebDriverWait(driver, 15).until( # Increased timeout
                EC.visibility_of_element_located(modal_selector)
            )
            take_screenshot(driver, "modal_appeared_successfully") # Screenshot after modal is found

            # Try to locate the username input field by a more specific ID
            # Common IDs could be 'username', 'recipient-username', 'share-username-input' etc.
            # Let's try 'recipient_username' as a placeholder.
            username_input_locator = (By.ID, 'recipient_username') 
            try:
                username_input = WebDriverWait(modal, 10).until(
                    EC.visibility_of_element_located(username_input_locator)
                )
            except TimeoutException:
                # Fallback: try by name if ID fails
                print(f"Could not find input by ID '{username_input_locator[1]}', trying by NAME 'username'...")
                username_input_locator = (By.NAME, 'username') # A common name attribute
                username_input = WebDriverWait(modal, 10).until(
                    EC.visibility_of_element_located(username_input_locator)
                )
            
            username_input.send_keys('test')
            
            # Find the share button within the modal context
            share_button_in_modal = WebDriverWait(modal, 10).until(
                EC.element_to_be_clickable((By.XPATH, './/button[contains(text(),"Share")]'))
            )
            share_button_in_modal.click()

            # Step 9: 登出
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.modal.show'))) # Ensure modal is gone

            logout_link_selector = (By.CSS_SELECTOR, 'ul.navbar-nav.ms-auto li.nav-item a.btn.btn-light')
            
            # Ensure logout link is present
            logout_link_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(logout_link_selector)
            )
            
            # Scroll logout link into view
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", logout_link_element)
            time.sleep(0.5) # Pause for smooth scroll

            # Wait for logout link to be clickable
            clickable_logout_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(logout_link_element)
            )
            take_screenshot(driver, "before_logout_click")

            try:
                # Use ActionChains for a more robust click
                actions = ActionChains(driver)
                actions.move_to_element(clickable_logout_link).click().perform()
                print("Clicked logout link using ActionChains.")
            except Exception as e:
                print(f"ActionChains click failed for logout link: {e}. Trying JavaScript click...")
                driver.execute_script("arguments[0].click();", clickable_logout_link)
                print("Clicked logout link using JavaScript.")
            
            time.sleep(1) # Give a moment for navigation to start after click

            # Wait for URL to be the landing page URL
            expected_landing_url = "http://localhost:5000/"
            try:
                WebDriverWait(driver, 15).until(EC.url_to_be(expected_landing_url))
                # As an additional check, wait for a known element on the landing page
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Discover Insights in Seconds')]"))
                )
                print(f"Successfully navigated to landing page: {driver.current_url}")
            except TimeoutException:
                take_screenshot(driver, "logout_redirect_failed")
                print(f"Timeout waiting for URL to be '{expected_landing_url}'. Current URL: {driver.current_url}")
                # Also print page source if redirect fails, for debugging
                # print(f"Page source at failure:\n{driver.page_source}")
                raise # Re-raise the exception to fail the test
            
            self.assertEqual(driver.current_url, expected_landing_url) # Explicitly check URL

        except (NoSuchElementException, TimeoutException) as e:
            take_screenshot(driver, "karen_error")
            self.fail(f"Karen流程失败: {str(e)}")

    def _test_user_verification(self):
        driver = self.driver
        try:
            # Step 10: Test用户登录
            driver.get("http://localhost:5000/login")
            driver.find_element(By.NAME, 'username').send_keys('test')
            driver.find_element(By.NAME, 'password').send_keys('password')
            driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            self.assertNotIn("Invalid credentials", driver.page_source)

            # Step 11: 访问 Shared 页面
            shared_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Shared']")))
            shared_link.click()

            # Step 12: 验证分享结果
            shared_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.card.my-3.shadow-sm')))
            self.assertGreaterEqual(len(shared_cards), 1)

            last_card = shared_cards[-1]
            from_text = last_card.find_element(By.CSS_SELECTOR, 'small.text-muted').text
            self.assertIn('From: karen', from_text)

        except (NoSuchElementException, TimeoutException) as e:
            take_screenshot(driver, "test_user_error")
            self.fail(f"Test用户验证失败: {str(e)}")


if __name__ == '__main__':
    unittest.main()
