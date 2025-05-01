import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

def DataWashing(df) -> pd.DataFrame:
    if isinstance(df, pd.DataFrame):
        clean_data_set = df.copy()
    else:
        clean_data_set = pd.read_csv(df)
    
    for column in clean_data_set.columns:
        # Check for too much missing values (over 50%)
        missing_ratio = clean_data_set[column].isna().mean()
        if missing_ratio > 0.5:
            clean_data_set.drop(column, axis=1, inplace=True)
            continue
            
        # Check column type
        numeric_count = clean_data_set[column].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x)).sum()
        string_count = clean_data_set[column].apply(lambda x: isinstance(x, str) and x.strip() != '').sum()
        total = len(clean_data_set[column])
        
        # Numeric feature handling
        if numeric_count / total > 0.5:
            # Convert to numeric, coerce errors to NaN
            clean_data_set[column] = pd.to_numeric(clean_data_set[column], errors='coerce')
            # Drop rows with non-numeric values
            clean_data_set = clean_data_set[clean_data_set[column].notna()]
            # Fill missing values
            imputer = SimpleImputer(strategy='mean')
            clean_data_set[column] = imputer.fit_transform(clean_data_set[[column]])
            
        # String feature handling
        elif string_count / total > 0.5:
            # Drop rows with non-string values
            clean_data_set = clean_data_set[clean_data_set[column].apply(lambda x: isinstance(x, str) and x.strip() != '')]
            # Encode string values
            le = LabelEncoder()
            clean_data_set[column] = le.fit_transform(clean_data_set[column])
            
        # Date feature handling (drop column)
        elif clean_data_set[column].apply(lambda x: isinstance(x, pd.Timestamp)).sum() / total > 0.5:
            clean_data_set.drop(column, axis=1, inplace=True)
            
    return clean_data_set
