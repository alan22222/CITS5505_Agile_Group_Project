import unittest
from flask import Flask, session
import sys
import os
# Try to import app moudle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app import create_app  # This is very important, other wise the whole test function would not work


class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key-for-session'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class TestSessionEncryption(unittest.TestCase):
    def setUp(self):
        # 创建 Flask 应用
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_secret_key_set(self):
        """Test whether secret key has been set up correctly"""
        self.assertEqual(self.app.config['SECRET_KEY'], 'test-secret-key-for-session')
        self.assertIsNotNone(self.app.secret_key)

    def test_session_is_encrypted(self):
        """Test whether session key has been loaded"""
        with self.app.test_request_context():
            session['username'] = 'testuser'

            s = self.app.session_interface.get_signing_serializer(self.app)

            signed_session = s.dumps(dict(session))

            self.assertNotIn('testuser', signed_session)
            print("Encrypted session cookie:", signed_session)

    def test_session_cookie_secure(self):
        """模拟请求，检查 session cookie 是否加密"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 12345

            # Start a request ro get cookie
            response = c.get('/')
            cookie = response.headers.get('Set-Cookie', '')

            # Check whether the session key is there
            self.assertIn('session=', cookie)

            # Check whether content is readable
            self.assertNotIn('user_id', cookie)
            print("Session cookie in headers:", cookie)

    def test_session_persists_and_decodes(self):
        """Test whether session can decode permantly"""
        with self.client as c:
            # Set up session key
            with c.session_transaction() as sess:
                sess['auth_token'] = 'abc123xyz'
            # Just a test
            response  = c.get('/')
            with c.session_transaction() as sess:
                self.assertEqual(sess.get('auth_token'), 'abc123xyz')


if __name__ == '__main__':
    unittest.main()
