import pandas as pd
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

def Linear_Regression_Training(file_csv, label_column, type):
    """
    Train a linear regression model with different configurations based on type.
    
    Args:
        file_csv (str): Path to CSV file
        label_column (int/str): Column index or name for label
        type (str): Training type ('Fast', 'Balance', 'High Precision')
        
    Returns:
        tuple: (result_dict, flag) where result_dict contains metrics and flag indicates success
    """
    try:
        # Read data
        df = pd.read_csv(file_csv)
        
        # Handle label column
        if isinstance(label_column, str):
            y = df[label_column]
            X = df.drop(columns=[label_column])
        else:
            y = df.iloc[:, label_column]
            X = df.drop(df.columns[label_column], axis=1)
            
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=None
        )
        
        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('sgdregressor', SGDRegressor(early_stopping=True, random_state=42))
        ])
        
        n_samples = len(X_train)
        
        if type == "Fast":
            params = {
                'sgdregressor__learning_rate': "constant",
                'sgdregressor__eta0': 0.001,
                'sgdregressor__max_iter': 1000,
                'sgdregressor__tol': 1e-4
            }
            pipeline.set_params(**params)
            pipeline.fit(X_train, y_train)
            
        elif type == "Balance":
            param_grid = {
                'sgdregressor__alpha': np.logspace(-2, 2, num=10).tolist(),
                'sgdregressor__l1_ratio': np.linspace(0.1, 0.9, num=9).tolist(),
                'sgdregressor__eta0': np.logspace(-4, -1, num=10).tolist(),
                'sgdregressor__batch_size': max(int(n_samples/20), 1),
                'sgdregressor__tol': [1e-4]
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
            
        elif type == "High Precision":
            param_grid = {
                'sgdregressor__alpha': np.logspace(-10, 10, num=100).tolist(),
                'sgdregressor__l1_ratio': np.linspace(0.1, 0.9, num=45).tolist(),
                'sgdregressor__eta0': np.logspace(-4, -1, num=50).tolist(),
                'sgdregressor__batch_size': max(int(n_samples/20), 1),
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
            
        else:
            raise ValueError("Invalid type. Must be 'Fast', 'Balance', or 'High Precision'")
        
        # Predict on validation set
        y_pred = pipeline.predict(X_val)
        
        # Calculate metrics
        mse = mean_squared_error(y_val, y_pred)
        
        result = {
            'MSE': mse,
            'precision': None  # Precision not typically used for regression
        }
        
        return result, True
        
    except Exception as e:
        print(f"Error in Linear_Regression_Training: {str(e)}")
        return {}, False
