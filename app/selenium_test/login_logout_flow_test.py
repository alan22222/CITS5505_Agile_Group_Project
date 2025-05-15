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
        # 创建内存数据库的Flask应用
        from config import TestConfig
        cls.app = create_app(config_class=TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        
        # 在单独的线程中启动Flask应用
        def run_flask_app():
            cls.app.run(host='127.0.0.1', port=5001, use_reloader=False)
            
        cls.flask_thread = threading.Thread(target=run_flask_app)
        cls.flask_thread.daemon = True  # 设置为守护线程，这样主线程结束时它会自动终止
        cls.flask_thread.start()
        print("Flask应用已在后台启动")
        sleep(1)  # 给Flask应用一点时间来启动

        # 配置Selenium
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # 明确指定Chrome路径
        
        # 使用Service对象配置驱动
        service = Service(executable_path='/opt/homebrew/bin/chromedriver')
        cls.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        cls.driver.implicitly_wait(10)  # 增加隐式等待时间

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        # 关闭Flask应用
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

        # 步骤1：访问首页
        driver.get("http://127.0.0.1:5001")
        
        # 步骤2-5：执行注册
        self._register_user(test_username, test_password, test_email)
        
        # 步骤6：验证注册成功
        self._verify_registration_success()

        # 步骤7-8：使用新账号登录
        self._login_user(test_username, test_password)
        
        # 步骤9：验证登录成功
        self._verify_login_success()

        # 步骤10：测试仪表盘所有链接
        self._test_dashboard_links()

        # 步骤11-12：执行登出并验证
        self._logout_and_verify()

    def _register_user(self, username, password, email):
        try:
            register_btn = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Register"))
            )
            register_btn.click()
        except Exception as e:
            self.fail(f"注册按钮点击失败: {str(e)}")

        # 填写注册表单
        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = self.driver.find_element(By.NAME, "password")
        email_field = self.driver.find_element(By.NAME, "email")

        username_field.send_keys(username)
        password_field.send_keys(password)
        email_field.send_keys(email)

        # 提交表单
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
            self.fail(f"注册验证失败: {str(e)}")

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
            self.fail(f"登录过程失败: {str(e)}")

    def _verify_login_success(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/dashboard"))
            welcome_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".welcome-header h2"))
            ).text
            self.assertIn("IamTestBot1", welcome_text)
        except Exception as e:
            self.fail(f"登录验证失败: {str(e)}")

    def _test_dashboard_links(self):
        try:
            test_links = [
                # 根据实际页面结构调整验证元素定位方式
                ("Upload Data", "/upload", (".container form", "上传表单")),
                ("Analyze", "/results", (".container .row", "分析结果区")),
                ("Shares", "/shared_with_me", (".container", "共享文件页面"))
            ]

            for link_text, expected_path, (element_locator, element_desc) in test_links:
                print(f"正在测试链接: {link_text}")
                try:
                    # 使用更稳定的定位方式
                    link = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, 
                            f"//a[contains(@class, 'action-button')]//span[@class='action-text' and normalize-space()='{link_text}']/ancestor::a")
                        )
                    )
                    
                    # 添加调试信息
                    print(f"元素定位成功，位置：{link.location}")
                    
                    # 使用带滚动和悬停的点击方式
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    ActionChains(self.driver)\
                        .move_to_element(link)\
                        .pause(1)\
                        .click()\
                        .perform()
                        
                    # 分步等待策略
                    # 1. 先等待URL变化
                    WebDriverWait(self.driver, 20).until(
                        EC.url_contains(expected_path)
                    )
                    print(f"成功跳转到：{self.driver.current_url}")
                    
                    # 2. 再等待目标元素可见
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, element_locator))
                    )
                    print(f"目标元素 {element_desc} 加载成功")
                    
                    # 返回操作加强验证
                    self.driver.back()
                    # 先等待URL变化
                    WebDriverWait(self.driver, 20).until(
                        EC.url_matches(r".*/dashboard/?.*")
                    )
                    # 再等待元素可见
                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".stats-container"))
                    )
                    print("成功返回仪表盘")
                    sleep(1)  # 保证DOM稳定
                    
                except Exception as e:
                    current_html = self.driver.page_source[:1000]
                    print(f"当前页面HTML片段：\n{current_html}")
                    self.driver.save_screenshot(f"{link_text.replace(' ', '_')}_error.png")
                    self.fail(f"链接 {link_text} 测试失败: {str(e)}\n当前URL: {self.driver.current_url}")

        except Exception as e:
            self.fail(f"仪表盘链接测试失败: {str(e)}")

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
            self.fail(f"登出过程失败: {str(e)}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
