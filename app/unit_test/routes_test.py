import unittest
import os
import tempfile
import shutil
import sys
from flask import url_for


# Import the root directory into flask app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)

from app import create_app
from app.models import db, User, UploadedData

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')  # 使用 TestConfig
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.create_test_user()

    def create_test_user(self):
        """Helper to create a test user."""
        user = User(
            username='testuser',
            email='test@example.com',
            password='hashed_password'
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        shutil.rmtree(self.app.config['UPLOAD_FOLDER'])

    def test_index_route(self):
        """Test root route '/'."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_route_get(self):
        """Test GET request to /register."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_register_route_post(self):
        """Test POST request to /register."""
        response = self.client.post('/register', data=dict(
            username='newuser',
            email='new@example.com',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'Registration successful!', response.data)

    def test_login_logout(self):
        """Test login and logout flow."""
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='wrong_password'
        ), follow_redirects=True)
        self.assertIn(b'Invalid credentials.', response.data)

        response = self.client.post('/login', data=dict(
            username='testuser',
            password='hashed_password'
        ), follow_redirects=True)
        self.assertIn(b'You were logged out', response.data)

    def test_dashboard_route_authenticated(self):
        """Test dashboard access after login."""
        self.login_user()
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_upload_route_get(self):
        """Test GET request to /upload."""
        self.login_user()
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)

    def test_upload_route_post(self):
        """Test POST request to /upload."""
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

        self.assertIn(b'Upload successful:', response.data)

    def test_select_model_get(self):
        """Test GET request to /select_model."""
        self.login_user()

        # Create dummy uploaded data
        uploaded_data = UploadedData(
            filename='test.csv',
            file_path='data.csv',
            file_size=1024,
            user_id=1
        )
        db.session.add(uploaded_data)
        db.session.commit()

        response = self.client.get('/select_model?data_id=1&suggested_col=1&filename=test.csv')
        self.assertEqual(response.status_code, 200)

    def test_select_model_post(self):
        """Test POST request to /select_model."""
        self.login_user()

        # Create dummy uploaded data
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

        # Since no ML model is mocked, it will fail but should redirect
        self.assertIn(b'Model execution failed:', response.data)

    def test_username_autocomplete(self):
        """Test username autocomplete route."""
        self.login_user()
        response = self.client.get('/username_autocomplete?q=test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('testuser', str(response.data))

    def login_user(self):
        return self.client.post('/login', data=dict(
            username='testuser',
            password='hashed_password'
        ), follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
