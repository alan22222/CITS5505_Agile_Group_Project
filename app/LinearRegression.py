import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

def LinearRegression(clean_content, label_column, type):
    """
    Train a linear regression model with different configurations.
    
    Args:
        file_csv (str): Path to CSV file
        label_column (str/int): Label column name or index
        type (str): Training type ('Fast', 'Balance', 'High Precision')
        
    Returns:
        tuple: (result_dict, flag) where result_dict contains metrics and flag indicates success
    """
    result = {
        'model_name': 'LinearRegression_SGD',
        'MSE_value': None,
        'precision_value': None
    }
    flag = False
    
    try:
        # Read data
        df = clean_content
        
        # Handle label column (could be name or index)
        if isinstance(label_column, int):
            y = df.iloc[:, label_column]
            X = df.drop(df.columns[label_column], axis=1)
        else:
            y = df[label_column]
            X = df.drop(label_column, axis=1)
            
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
        )
        
        # Create pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('sgdregressor', SGDRegressor(early_stopping=True, random_state=42))
        ])
        
        n_samples = len(X_train)
        
        if type == 'Fast':
            params = {
                'sgdregressor__learning_rate': ['constant'],
                'sgdregressor__eta0': np.float64(0.001),
                'sgdregressor__max_iter': [1000],
                'sgdregressor__tol': [1e-4]
            }
            pipeline.set_params(**params)
            pipeline.fit(X_train, y_train)
            
        elif type in ['Balance', 'High Precision']:
            # Define parameter grid based on type
            if type == 'Balance':
                param_grid = {
                    'sgdregressor__alpha': np.logspace(-2, 2, num=10).tolist(),
                    'sgdregressor__l1_ratio': np.linspace(0.1, 0.9, num=9).tolist(),
                    'sgdregressor__eta0': np.logspace(-4, -1, num=10).tolist(),
                    
                    'sgdregressor__tol': [1e-4]
                }
            else:  # High Precision
                param_grid = {
                    'sgdregressor__alpha': np.logspace(-10, 10, num=20).tolist(),
                    'sgdregressor__l1_ratio': np.linspace(0.1, 0.9, num=45).tolist(),
                    'sgdregressor__eta0': np.logspace(-4, -1, num=10).tolist(),
                    
                    'sgdregressor__tol': [1e-5, 1e-6]
                }
            
            grid_search = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                cv=5,
                scoring='neg_mean_squared_error',
                n_jobs=-1,
                verbose=2
            )
            grid_search.fit(X_train, y_train)
            pipeline = grid_search.best_estimator_
        
        # Evaluate on validation set
        y_pred = pipeline.predict(X_val)
        result['MSE_value'] = mean_squared_error(y_val, y_pred)
        result['precision_value'] = r2_score(y_val, y_pred)
        flag = True
        
    except Exception as e:
        result = str(e)
        flag = False
        
    return result, flag
