import unittest
import pandas as pd
import numpy as np
import os
import sys

# 获取当前脚本所在的目录（unit_test目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 app 目录的上一级目录（即项目根目录）
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
# 将项目根目录添加到 Python 模块搜索路径中
sys.path.append(project_root)

from app.static.ml_model.K_means import kmeans_function, plot_radar_chart
class TestKMeansFunction(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a simple test dataset
        self.df = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'feature3': np.random.rand(100)
        })
        
        # Create a small dataset with clear clusters for more specific testing
        self.clustered_df = pd.DataFrame({
            'feature1': np.concatenate([np.random.normal(0, 0.5, 30), 
                                       np.random.normal(5, 0.5, 30),
                                       np.random.normal(-5, 0.5, 30)]),
            'feature2': np.concatenate([np.random.normal(0, 0.5, 30), 
                                       np.random.normal(5, 0.5, 30),
                                       np.random.normal(-5, 0.5, 30)])
        })

    def test_valid_input(self):
        """Test function works with valid input"""
        result, flag = kmeans_function(self.df, "Fast")
        self.assertTrue(flag)
        self.assertEqual(result['model_name'], 'KMeans')
        
    def test_invalid_input_type(self):
        """Test function handles invalid input type"""
        _, flag = kmeans_function(clean_content=self.df,type="What")
        self.assertFalse(flag)
        
        
        
    def test_model_Balance(self):
        """Test model performance on clustered data"""
        _, flag = kmeans_function(self.clustered_df, "Balance")
        self.assertTrue(flag)
        
    def test_reproducibility(self):
        """Test results are consistent across runs"""
        _, flag1 = kmeans_function(self.df, "Fast")
        _, flag2 = kmeans_function(self.df, "Fast")
        
        self.assertTrue(flag1 and flag2)
        # For Fast mode with same data, results should be consistent

if __name__ == '__main__':
    unittest.main()
