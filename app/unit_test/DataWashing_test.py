import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
# Add root directory into test program
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
from app.static.ml_model.DataWashing import DataWashing


class TestDataWashing(unittest.TestCase):
    
    def test_valid_dataframe_input(self):
        # Create a sample dataframe with different issues
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', 'b', 'c', np.nan, 'e'],
            'C': [np.nan] * 5,  # Column with all NaNs
            'D': [1, '2', 3, 4, 5],  # Mixed types
            'E': pd.date_range('2023-01-01', periods=5)  # Date column
        })
        
        result = DataWashing(df)
        
        # Check that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that columns with >50% missing values are dropped
        self.assertNotIn('C', result.columns)
        
        # Check that date column is dropped
        self.assertNotIn('E', result.columns)
        
        # Check that numeric column has no missing values
        self.assertFalse(result['A'].isna().any())
        
        # Check that string column is encoded
        self.assertTrue(all(isinstance(x, int) for x in result['B']))
        
        # Check that mixed type column is handled
        self.assertFalse(result['D'].apply(lambda x: isinstance(x, str)).any())
    
    def test_valid_file_path_input(self):
        # Create a temporary CSV file
        data = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['a', 'b', 'c', np.nan, 'e']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            data.to_csv(f.name, index=False)
            
            result = DataWashing(f.name)
            
            # Check that the result is a DataFrame
            self.assertIsInstance(result, pd.DataFrame)
            
            # Check that no columns were dropped unexpectedly
            self.assertEqual(len(result.columns), 2)
            
            # Check that numeric column has no missing values
            self.assertFalse(result['A'].isna().any())
        
        # Clean up the temporary file
        os.unlink(f.name)
    
    def test_invalid_input(self):
        # Test with invalid input (neither DataFrame nor file path)
        result = DataWashing(123)
        
        # Check that the result is None
        self.assertIsNone(result)
    
    def test_file_not_found(self):
        # Test with non-existent file
        result = DataWashing("nonexistent_file.csv")
        
        # Check that the result is None
        self.assertIsNone(result)
    
    def test_mixed_values_handling(self):
        # Create a dataframe with mixed numeric and string values
        df = pd.DataFrame({
            'A': [1, '2', 3, 'invalid', 5],
            'B': ['a', 1, 'c', 2, 'e']
        })
        
        result = DataWashing(df)
        
        # Check that the result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check that numeric column A is numeric with no missing values
        self.assertTrue(pd.api.types.is_numeric_dtype(result['A']))
        self.assertFalse(result['A'].isna().any())
        
        # Check that column B is treated as string and encoded
        self.assertTrue(all(isinstance(x, int) for x in result['B']))
    def ten_columns_testing(self):
        num_rows = 1000  # A extreme large value for instances
        num_cols = 9   # A medium value for features
        names = [f"Person_{i+1}" for i in range(num_rows)]
        # Generate data randomly to see whether function can handle that
        data = {}
        for i in range(num_cols):
            if i % 2 == 0:
                data[f"Int_Var_{i+1}"] = np.random.randint(0, 100, size=num_rows)
            else:
                data[f"Float_Var_{i+1}"] = np.round(np.random.rand(num_rows) * 100, 2)
        # Building DataFrame now
        df = pd.DataFrame(data)
        df.insert(0, 'Name', names)  # 插入名称列到第一列


if __name__ == '__main__':
    unittest.main()
