import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

def DataWashing(df):
    """
    Clean and preprocess a pandas DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame to be cleaned
        
    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    clean_df = df.copy()
    
    for col in clean_df.columns:
        # Check for too much missing values (>50%)
        missing_ratio = clean_df[col].isna().mean()
        if missing_ratio > 0.5:
            clean_df.drop(col, axis=1, inplace=True)
            continue
            
        # Check column type
        col_type = clean_df[col].dtype
        
        # Numeric feature handling
        if pd.api.types.is_numeric_dtype(col_type):
            # Check if >50% are numeric
            numeric_ratio = clean_df[col].apply(lambda x: isinstance(x, (int, float))).mean()
            if numeric_ratio > 0.5:
                # Drop non-numeric rows
                clean_df = clean_df[pd.to_numeric(clean_df[col], errors='coerce').notna()]
                # Impute missing values
                imputer = SimpleImputer(strategy='mean')
                clean_df[col] = imputer.fit_transform(clean_df[[col]])
        
        # String feature handling
        elif pd.api.types.is_string_dtype(col_type):
            # Check if >50% are strings
            string_ratio = clean_df[col].apply(lambda x: isinstance(x, str)).mean()
            if string_ratio > 0.5:
                # Drop non-string rows
                clean_df = clean_df[clean_df[col].apply(lambda x: isinstance(x, str))]
                # Encode strings to integers
                le = LabelEncoder()
                clean_df[col] = le.fit_transform(clean_df[col])

                # Check string frequency and drop column if any string appears less than 3 times
                string_counts = clean_df[col].value_counts()
                if any(string_counts < 3):
                    clean_df.drop(col, axis=1, inplace=True)
                    continue
        
        # Date feature handling
        elif pd.api.types.is_datetime64_any_dtype(col_type):
            # Drop date columns if >50% are dates
            date_ratio = clean_df[col].apply(lambda x: pd.api.types.is_datetime64_any_dtype(x)).mean()
            if date_ratio > 0.5:
                clean_df.drop(col, axis=1, inplace=True)
        
        # Abnormal string handling (non-alphanumeric)
        else:
            # Check for abnormal strings
            abnormal_ratio = clean_df[col].apply(
                lambda x: isinstance(x, str) and not x.isalnum()
            ).mean()
            if abnormal_ratio > 0.5:
                clean_df.drop(col, axis=1, inplace=True)
    
    # Print column indices with non-numeric content
    for col in clean_df.columns:
        if any(~clean_df[col].apply(lambda x: str(x).isdigit())):
            print(f"Column with non-numeric content: {col}")
    
    return clean_df
