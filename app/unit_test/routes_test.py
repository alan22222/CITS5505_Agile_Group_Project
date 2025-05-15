import unittest
import os
import sys
import tempfile
import shutil
from flask import url_for

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)

from app import create_app
from app.models import db, User, UploadedData


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Using test config for our unit test
        self.app = create_app('testing')  
        # Make sure we are using memory database rather than the real one
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.create_test_user()

    def create_test_user(self):
        """Helper to create a test user."""
        user = User(
            username='testuser_Yanchen',
            email='testYanchen@example.com',
            password='hashed_secret_password'
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        shutil.rmtree(self.app.config['UPLOAD_FOLDER'], ignore_errors=True)


    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_route_get(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_route_post(self):
        response = self.client.post('/register', data=dict(
            username='newuser',
            email='new@example.com',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'Registration successful!', response.data)

    def test_login_logout(self):
        response = self.client.post('/login', data=dict(
            username='testuser_Yanchen',
            password='wrong_password'
        ), follow_redirects=True)
        self.assertIn(b'Invalid credentials.', response.data)

        response = self.client.post('/login', data=dict(
            username='testuser_Yanchen',
            password='hashed_secret_password'
        ), follow_redirects=True)
        self.assertIn(b'Welcome', response.data)  

    def test_dashboard_route_authenticated(self):
        self.login_user()
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_upload_route_get(self):
        self.login_user()
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 302)

    def test_upload_route_post(self):
        self.login_user()

        # Create a temporary CSV file
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', dir=self.app.config['UPLOAD_FOLDER'], delete=False)
        temp_file.write(b"name,age\nAlice,30\nBob,25")
        temp_file.close()

        with open(temp_file.name, 'rb') as f:
            response = self.client.post('/upload', data=dict(
                file=f,
                text='',
                upload_name='test_csv'
            ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_select_model_get(self):
        """Test GET request to /select_model."""
        self.login_user()
        with self.app.app_context():
            uploaded_data = UploadedData(
                filename='test.csv',
                file_path='data.csv',
                file_size=1024,
                user_id=1
            )
            db.session.add(uploaded_data)
            db.session.commit()

        response = self.client.get('/select_model?data_id=1&suggested_col=1&filename=test.csv')
        self.assertEqual(response.status_code, 302)

    def test_select_model_post(self):
        """Test POST request to /select_model."""
        self.login_user()
        with self.app.app_context():
            uploaded_data = UploadedData(
                filename='test.csv',
                file_path='data.csv',
                file_size=1024,
                user_id=1
            )
            db.session.add(uploaded_data)
            db.session.commit()

        response = self.client.post('/select_model', data=dict(
            user_id=1,
            model_type='linear_regression',
            precision_mode='Fast',
            target_index=1,
            has_header=True,
            file_select='test.csv'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_username_autocomplete(self):
        self.login_user()
        response = self.client.get('/username_autocomplete?q=test')
        self.assertEqual(response.status_code, 302)

    def login_user(self):
        return self.client.post('/login', data=dict(
            username='testuser_Yanchen',
            password='hashed_secret_password'
        ), follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
