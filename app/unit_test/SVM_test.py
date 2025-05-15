import unittest
import pandas as pd
import numpy as np
import os
import sys
import uuid
import shutil
from flask import Flask

# Import the root directory into flask app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from app.static.ml_model.SVM_classifier import SVMClassifier  # Replace 'your_module_name' with the actual module name
class TestSVMClassifier(unittest.TestCase):
    """
    Unit tests for SVMClassifier function.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up test environment before running all tests.
        """
        # Create sample data for testing
        np.random.seed(42)
        cls.num_samples = 100
        cls.num_features = 5
        
        # Generate random data
        cls.data = np.random.rand(cls.num_samples, cls.num_features)
        cls.labels = np.random.randint(0, 2, size=cls.num_samples)
        
        # Create DataFrame
        cls.df = pd.DataFrame(cls.data, columns=[f"feature_{i}" for i in range(cls.num_features)])
        cls.df['label'] = cls.labels
        
        # Create temporary directory for plots
        cls.plot_dir = 'test_plotting'
        if os.path.exists(cls.plot_dir):
            shutil.rmtree(cls.plot_dir)
        os.makedirs(cls.plot_dir)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after all tests have finished.
        """
        # Remove temporary directory
        if os.path.exists(cls.plot_dir):
            shutil.rmtree(cls.plot_dir)

    def setUp(self):
        """
        Set up before each test.
        """
        # Create a fresh copy of the DataFrame for each test
        self.test_df = self.df.copy()
        
        # Set the label column
        self.label_column = 'label'
        
        # Mock UUID to make plot paths predictable for testing
        self.original_uuid = uuid.uuid4
        uuid.uuid4 = lambda: uuid.UUID('12345678123456781234567812345678')

    def tearDown(self):
        """
        Clean up after each test.
        """
        # Remove any generated plots
        for root, dirs, files in os.walk(self.plot_dir):
            for file in files:
                if file.endswith(".png"):
                    os.remove(os.path.join(root, file))
        
        # Restore original UUID function
        uuid.uuid4 = self.original_uuid

    def test_valid_input_with_dataframe(self):
        """
        Test that SVMClassifier runs successfully with valid DataFrame input.
        """
        app = Flask(__name__)
        with app.app_context():
            result, success = SVMClassifier(self.test_df, self.label_column, "Fast")
            
            # Check if execution was successful
            self.assertTrue(success)
            
            # Check result structure
            self.assertIsInstance(result, dict)
            self.assertIn('model_name', result)
            self.assertIn('Precision_value', result)
            self.assertIn('Accuracy_value', result)
            self.assertIn('Recall_value', result)
            self.assertIn('F1_score_value', result)
            self.assertIn('plot_path', result)
            
            
            # Check metric values are within valid range
            self.assertTrue(0 <= result['Precision_value'] <= 1)
            self.assertTrue(0 <= result['Accuracy_value'] <= 1)
            self.assertTrue(0 <= result['Recall_value'] <= 1)
            self.assertTrue(0 <= result['F1_score_value'] <= 1)

    def test_valid_input_with_column_index(self):
        """
        Test that SVMClassifier works when label_column is provided as an index.
        """
        # Use the last column as label
        app = Flask(__name__)
        with app.app_context():
            result, success = SVMClassifier(self.test_df, self.test_df.shape[1] - 1, "Fast")
            
            self.assertTrue(success)
            self.assertIsInstance(result, dict)

    def test_invalid_input_type(self):
        """
        Test that SVMClassifier raises error when input data is not a DataFrame.
        """
        # Pass a numpy array instead of DataFrame
        app = Flask(__name__)
        with app.app_context():
            result, success = SVMClassifier(self.data, self.label_column, "Fast")
            
            # Check for failure
            self.assertFalse(success)
            self.assertIn("The input data should be a pandas.DataFrame variable", result)

    def test_invalid_label_column(self):
        """
        Test that SVMClassifier handles invalid label column names/indices.
        """
        # Use a non-existent column name
        app = Flask(__name__)
        with app.app_context():
            _, success = SVMClassifier(self.test_df, "invalid_column_name", "Fast")
            self.assertFalse(success)
            
            # Use an out-of-range column index
            _, success = SVMClassifier(self.test_df, 999, "Fast")
            self.assertFalse(success)

    def test_different_types(self):
        """
        Test that SVMClassifier works with all three type options.
        """
        app = Flask(__name__)
        with app.app_context():
            for model_type in ["Fast", "Balance", "High Precision"]:
                with self.subTest(model_type=model_type):
                    result, success = SVMClassifier(self.test_df, self.label_column, model_type)
                    self.assertTrue(success)
                    self.assertIsInstance(result, dict)
                    
                    # Verify model name
                    self.assertEqual(result['model_name'], 'SVMClassifier')
                    
                    self.assertEqual(success, True)


if __name__ == '__main__':
    unittest.main()
