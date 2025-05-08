import unittest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score
import os
import sys
import shutil
import uuid
import warnings

# 忽略UserWarning
warnings.filterwarnings("ignore", category=UserWarning)

# 导入待测试模块
# 获取当前脚本所在的目录（unit_test目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取 app 目录的上一级目录（即项目根目录）
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
# 将项目根目录添加到 Python 模块搜索路径中
sys.path.append(project_root)

from app.static.ml_model.SVM_classifier import SVMClassifier

class TestSVMClassifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """创建测试数据集"""
        # 创建3个不同的测试数据集用于三轮测试
        X1, y1 = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=42)
        X2, y2 = make_classification(
            n_samples=500, n_features=20, n_classes=3, n_informative=4, random_state=43
        )
        X3, y3 = make_classification(
            n_samples=1000, n_features=15, n_classes=4, n_informative=5, random_state=44
        )
        
        cls.datasets = [
            (pd.DataFrame(np.hstack((X1, y1.reshape(-1, 1)))), "label", "Fast"),
            (pd.DataFrame(np.hstack((X2, y2.reshape(-1, 1)))), 20, "Balance"),
            (pd.DataFrame(np.hstack((X3, y3.reshape(-1, 1)))), "label", "High Precision")
        ]
        
        # 添加列名以方便测试DataFrame输入的情况
        for i, (df, label_col, _) in enumerate(cls.datasets):
            if isinstance(label_col, str):
                df.columns = [f"feature_{j}" for j in range(df.shape[1]-1)] + [label_col]
    
    @classmethod
    def tearDownClass(cls):
        """清理生成的文件和目录"""
        if os.path.exists('./static/plotting/'):
            shutil.rmtree('./static/plotting/')
    
    def test_SVMClassifier_dataframe_input(self):
        """测试使用DataFrame输入的情况"""
        # 修改第一个测试用例使用DataFrame输入
        df, label_col, type_ = self.datasets[0]
        
        result, success = SVMClassifier(df, label_col, type_)
        
        self.assertTrue(success)
        self.assertIsInstance(result, dict)
        self.assertIn('model_name', result)
        self.assertIn('Precision_value', result)
        self.assertIn('Accuracy_value', result)
        self.assertIn('Recall_value', result)
        self.assertIn('F1_score_value', result)
        self.assertIn('plot_path', result)
        
        # 检查指标值是否在合理范围内
        self.assertTrue(0 <= result['Precision_value'] <= 1)
        self.assertTrue(0 <= result['Accuracy_value'] <= 1)
        self.assertTrue(0 <= result['Recall_value'] <= 1)
        self.assertTrue(0 <= result['F1_score_value'] <= 1)
        
        # 检查是否生成了图表文件
        self.assertTrue(os.path.exists(result['plot_path']))
    
    def test_SVMClassifier_column_index(self):
        """测试使用列索引作为标签列的情况"""
        df, label_idx, type_ = self.datasets[1]
        
        result, success = SVMClassifier(df, label_idx, type_)
        
        self.assertTrue(success)
        self.assertIsInstance(result, dict)
        self.assertIn('model_name', result)
        self.assertIn('Precision_value', result)
        self.assertIn('Accuracy_value', result)
        self.assertIn('Recall_value', result)
        self.assertIn('F1_score_value', result)
        self.assertIn('plot_path', result)
        
        # 检查指标值是否在合理范围内
        self.assertTrue(0 <= result['Precision_value'] <= 1)
        self.assertTrue(0 <= result['Accuracy_value'] <= 1)
        self.assertTrue(0 <= result['Recall_value'] <= 1)
        self.assertTrue(0 <= result['F1_score_value'] <= 1)
        
        # 检查是否生成了图表文件
        self.assertTrue(os.path.exists(result['plot_path']))
    
    def test_SVMClassifier_high_precision_mode(self):
        """测试High Precision模式下的参数搜索"""
        df, label_col, type_ = self.datasets[2]
        
        result, success = SVMClassifier(df, label_col, type_)
        
        self.assertTrue(success)
        self.assertIsInstance(result, dict)
        self.assertIn('model_name', result)
        self.assertIn('Precision_value', result)
        self.assertIn('Accuracy_value', result)
        self.assertIn('Recall_value', result)
        self.assertIn('F1_score_value', result)
        self.assertIn('plot_path', result)
        
        # 检查指标值是否在合理范围内
        self.assertTrue(0 <= result['Precision_value'] <= 1)
        self.assertTrue(0 <= result['Accuracy_value'] <= 1)
        self.assertTrue(0 <= result['Recall_value'] <= 1)
        self.assertTrue(0 <= result['F1_score_value'] <= 1)
        
        # 检查是否生成了图表文件
        self.assertTrue(os.path.exists(result['plot_path']))
    
    def test_invalid_input_data(self):
        """测试无效的输入数据类型"""
        df, label_col, _ = self.datasets[0]
        
        # 传递非DataFrame对象
        result, success = SVMClassifier("invalid_data", label_col, "Fast")
        
        self.assertFalse(success)
        self.assertIsInstance(result, str)
        self.assertIn("The input data should be a pandas.DataFrame variable", result)
    
    def test_invalid_label_column(self):
        """测试无效的标签列"""
        df, _, _ = self.datasets[0]
        
        # 传递不存在的列名
        result, success = SVMClassifier(df, "invalid_column", "Fast")
        
        self.assertFalse(success)
        self.assertIsInstance(result, str)
        self.assertIn("KeyError", result)

if __name__ == '__main__':
    unittest.main()
