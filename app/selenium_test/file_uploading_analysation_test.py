# 文件路径：app/selenium_test/file_uploading_analysation_test.py
import unittest
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select


def get_project_root():
    """返回项目根目录路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(current_dir, '..', '..'))
class AnalysisTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 获取项目根目录
        cls.project_root = get_project_root()
        sys.path.insert(0, cls.project_root)
        
        # 配置浏览器驱动
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        
        cls.driver = webdriver.Chrome(
            service=Service(executable_path='/opt/homebrew/bin/chromedriver'),
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:5001"
        
        # 测试文件路径
        cls.test_file = os.path.join(
            cls.project_root,
            'tests',
            'regression_data.csv'
        )
        print(f"测试文件路径验证：{cls.test_file}")  # 调试用
    def test_01_full_workflow(self):
        """完整工作流测试"""
        driver = self.driver
        
        # 阶段1：登录
        driver.get(f"{self.base_url}/login")
        driver.find_element(By.NAME, 'username').send_keys('Yanchen')
        driver.find_element(By.NAME, 'password').send_keys('password')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        # 验证登录
        WebDriverWait(driver, 10).until(
            EC.url_contains('/dashboard'))
        self.assertIn('/dashboard', driver.current_url)
        
        # 阶段2：文件上传
        driver.get(f"{self.base_url}/upload")
        file_input = driver.find_element(By.ID, 'fileUpload')
        file_input.send_keys(self.test_file)
        # Use JavaScript click to avoid interception issues
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        driver.execute_script("arguments[0].click();", submit_button)
        
        # 验证上传成功
        WebDriverWait(driver, 10).until(
            EC.url_contains('/select_model'))
        self.assertIn('/select_model', driver.current_url)
        
        # 阶段3：模型配置
        # Select the uploaded file from the dropdown
        uploaded_filename = os.path.basename(self.test_file)
        Select(driver.find_element(By.NAME, 'file_select')).select_by_visible_text(uploaded_filename)

        Select(driver.find_element(By.NAME, 'model_type')
            ).select_by_visible_text('Linear Regression')
        Select(driver.find_element(By.NAME, 'precision_mode')
            ).select_by_visible_text('Fast')
        driver.find_element(By.NAME, 'target_index').send_keys('1')
        # Use JavaScript click to avoid interception issues
        submit_button_model_config = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        driver.execute_script("arguments[0].click();", submit_button_model_config)
        
        # 验证结果页
        WebDriverWait(driver, 15).until(
            EC.url_contains('/results'))
        self.assertIn('/results', driver.current_url)

    def test_02_result_view(self):
        """结果查看测试"""
        driver = self.driver
        
        # 直接访问结果页
        driver.get(f"{self.base_url}/results")
        self.assertIn('/results', driver.current_url)
        
        # 查找并点击第一个View按钮
        # Wait for the first 'View' button to be clickable
        first_view_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '(//a[contains(text(), "View")])[1]'))
        )
        first_view_button.click()
        
        # 验证详情页加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'model-container')))
        
        # 注销操作
        driver.find_element(By.LINK_TEXT, 'Logout').click()
        WebDriverWait(driver, 10).until(
            EC.url_matches(f"{self.base_url}/")) # Expecting root URL after logout
        self.assertEqual(driver.current_url, f"{self.base_url}/") # Assert exact root URL

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == '__main__':
    unittest.main()
