import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib
import matplotlib.pyplot as plt
import os
import uuid

def LinearRegressionTraining(clean_data, label_column, type):
    try:
        if isinstance(clean_data, pd.DataFrame):
            df = clean_data
        else:
            raise TypeError("The input data should be a pandas.DataFrame variable")
        # Handle label column (could be index or name)
        if isinstance(label_column, str):
            y = df[label_column]
            label_column = df.columns.get_loc(label_column)
            X = df.drop(df.columns[label_column], axis=1)
            
        else:
            y = df.iloc[:, label_column]
            X = df.drop(df.columns[label_column], axis=1)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True)
        matplotlib.use('Agg') # Make sure plotting method will not be blocked by MacOS
        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('sgdregressor', SGDRegressor(early_stopping=True, random_state=42))
        ])
        
        # Different parameters based on type
        if type == "Fast":
            params = {
                'sgdregressor__learning_rate': 'constant',
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
                'sgdregressor__alpha': np.logspace(-10, 10, num=20).tolist(),
                'sgdregressor__l1_ratio': np.linspace(0.1, 0.9, num=45).tolist(),
                'sgdregressor__eta0': np.logspace(-4, -1, num=20).tolist(),
                
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
        
        # Predict and calculate metrics
        y_pred = pipeline.predict(X_val)
        mse = mean_squared_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        print("========================Analysation Process Done, Plotting data=========================")

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.scatter(range(len(y_val)), y_val, color='blue', label='Actual')
        plt.plot(range(len(y_val)), y_pred, color='red', linewidth=2, label='Predicted')
        plt.title('Linear Regression Results')
        plt.xlabel('Sample Index')
        plt.ylabel('Target Value')
        plt.legend()
        
        # Save plot
        os.makedirs('app/plotting/', exist_ok=True)
        plot_path = f'app/plotting/{uuid.uuid4()}.png'
        plt.savefig(plot_path)
        plt.close()
        
        # Prepare result
        result = {
            'model_name': 'LinearRegression',
            'MSE_value': mse,
            'speed_mode': type,
            'label_index': label_column,
            'has_header': False,
            
            'precision_value': r2,
            'plot_path': plot_path
        }
        
        return result, True
    
    except Exception as e:
        error_message = f"Error during Linear Regression training: {str(e)}"
        print(error_message)
        result = error_message
        return result, False
