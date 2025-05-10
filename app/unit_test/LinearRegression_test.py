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

from app.static.ml_model.LinearRegression import LinearRegressionTraining

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
        print("Test data setted up already")
        print(self.test_data)
    def test_check_column_input_valid_string(self):
        """Test check_column_input with valid string column name"""
        _, flag = LinearRegressionTraining(clean_data=self.test_data, label_column='target', type="Fast")
        self.assertEqual(flag, True)
    
    def test_check_column_input_valid_index(self):
        """Test check_column_input with valid column index"""
        _, flag = LinearRegressionTraining(clean_data=self.test_data, label_column=1, type="Fast")
        self.assertEqual(flag, True)
    
    def test_check_column_input_invalid_string(self):
        """Test check_column_input with invalid column name"""
        _, flag = LinearRegressionTraining(clean_data=self.test_data, label_column='NaughtyLabel', type="Fast")
        self.assertEqual(flag, False)
    
    def test_check_column_input_invalid_index(self):
        """Test check_column_input with invalid column index"""
        _, flag = LinearRegressionTraining(clean_data=self.test_data, label_column=100, type="Fast")
        self.assertEqual(flag, False)
    
    
    def test_check_column_invalid_type(self):
        """Test check_column_input with invalid input type"""
        _, flag = LinearRegressionTraining(clean_data=self.test_data, label_column=1.3, type="Fast")
        self.assertEqual(flag, False)
    
    
    def test_ckech_invalid_datainput(self):
        """Test function with invalid input data"""
        empty_data = pd.DataFrame()
        _, flag = LinearRegressionTraining(clean_data=empty_data, label_column=1.3, type="Fast")
        self.assertEqual(flag, False)
if __name__ == '__main__':
    unittest.main()
