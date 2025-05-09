import unittest
import pandas as pd
import numpy as np
import os
import sys
import uuid
# 获取当前脚本所在的目录（unit_test目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 app 目录的上一级目录（即项目根目录）
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
# 将项目根目录添加到 Python 模块搜索路径中
sys.path.append(project_root)

from app.static.ml_model.LinearRegression import LinearRegressionTraining, check_column_input

class TestLinearRegression(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create a simple test dataset
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'target': np.random.rand(100)
        })
        
        # Create a dataset with numeric columns for index testing
        self.numeric_data = pd.DataFrame(np.random.rand(100, 5))
    
    def test_check_column_input_valid_string(self):
        """Test check_column_input with valid string column name"""
        self.assertTrue(check_column_input(self.test_data, 'feature1'))
    
    def test_check_column_input_valid_index(self):
        """Test check_column_input with valid column index"""
        self.assertTrue(check_column_input(self.test_data, 0))
    
    def test_check_column_input_invalid_string(self):
        """Test check_column_input with invalid column name"""
        with self.assertWarns(UserWarning):
            self.assertFalse(check_column_input(self.test_data, 'invalid_column'))
    
    def test_check_column_input_invalid_index(self):
        """Test check_column_input with invalid column index"""
        with self.assertWarns(UserWarning):
            self.assertFalse(check_column_input(self.test_data, 10))
    
    def test_check_column_input_multiple_columns(self):
        """Test check_column_input with multiple columns"""
        self.assertTrue(check_column_input(self.test_data, ['feature1', 'feature2']))
    
    def test_check_column_input_mixed_types(self):
        """Test check_column_input with mixed string and integer types"""
        with self.assertWarns(UserWarning):
            self.assertFalse(check_column_input(self.test_data, ['feature1', 0]))
    
    def test_check_column_invalid_type(self):
        """Test check_column_input with invalid input type"""
        with self.assertWarns(UserWarning):
            self.assertFalse(check_column_input(self.test_data, 3.14))
    
    def test_linear_regression_training_with_string_label(self):
        """Test LinearRegressionTraining with string label column"""
        result, success = LinearRegressionTraining(self.test_data, 'target', 'Fast')
        self.assertTrue(success)
        self.assertIn('MSE_value', result)
        self.assertIn('precision_value', result)
        self.assertTrue(os.path.exists(result['plot_path']))
    
    def test_linear_regression_training_with_index_label(self):
        """Test LinearRegressionTraining with index label column"""
        result, success = LinearRegressionTraining(self.numeric_data, 4, 'Fast')
        self.assertTrue(success)
        self.assertIn('MSE_value', result)
        self.assertIn('precision_value', result)
        self.assertTrue(os.path.exists(result['plot_path']))
    
    def test_linear_regression_training_invalid_label(self):
        """Test LinearRegressionTraining with invalid label column"""
        result, success = LinearRegressionTraining(self.test_data, 'invalid_column', 'Fast')
        self.assertFalse(success)
        self.assertIn('Error during Linear Regression training', result)
    
    def test_linear_regression_training_invalid_data_type(self):
        """Test LinearRegressionTraining with invalid data type"""
        result, success = LinearRegressionTraining("not_a_dataframe", 'target', 'Fast')
        self.assertFalse(success)
        self.assertIn('Error during Linear Regression training', result)
    
    def test_linear_regression_training_different_types(self):
        """Test LinearRegressionTraining with different types (Fast, Balance, High Precision)"""
        for reg_type in ["Fast", "Balance", "High Precision"]:
            with self.subTest(reg_type=reg_type):
                result, success = LinearRegressionTraining(self.test_data, 'target', reg_type)
                self.assertTrue(success)
                self.assertIn('MSE_value', result)
                self.assertIn('precision_value', result)
                self.assertTrue(os.path.exists(result['plot_path']))
    
    def tearDown(self):
        """Clean up generated plot files"""
        if os.path.exists('./static/plotting/'):
            for file in os.listdir('./static/plotting/'):
                if file.endswith('.png'):
                    try:
                        os.remove(os.path.join('./static/plotting/', file))
                    except PermissionError:
                        pass  # Skip files that can't be deleted

if __name__ == '__main__':
    unittest.main()
