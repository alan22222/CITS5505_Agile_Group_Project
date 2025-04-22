from sklearn.svm import LinearSVC
from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
import pandas as pd
import numpy as np

def SVM_classifier(file_csv, label_column, type):
    """
    Train an SVM classifier with different configurations based on type.
    
    Args:
        file_csv (str): Path to CSV file
        label_column (int/str): Column index or name for label
        type (str): Training type ('Fast', 'Balance', 'High Precision')
        
    Returns:
        tuple: (result_list, flag) where result_list contains metrics and flag indicates success
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
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create pipeline with scaling
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('svm', LinearSVC(random_state=42))
        ])
        
        if type == "Fast":
            params = {
                'svm__C': 1,
                'svm__loss': 'hinge',
                'svm__max_iter': 500,
                'svm__tol': 1e-3
            }
            pipeline.set_params(**params)
            pipeline.fit(X_train, y_train)
            
        elif type == "Balance":
            param_grid = {
                'svm__C': [0.1, 1, 10],
                'svm__penalty': ['l1', 'l2'],
                'svm__loss': ['hinge', 'squared_hinge'],
                'svm__max_iter': [1000],
                'svm__tol': [1e-3, 1e-4]
            }
            
            grid_search = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1,
                verbose=2
            )
            grid_search.fit(X_train, y_train)
            pipeline = grid_search.best_estimator_
            
        elif type == "High Precision":
            param_grid = {
                'svm__C': np.linspace(0.1, 10, num=100).tolist(),
                'svm__penalty': ['l1', 'l2'],
                'svm__loss': ['hinge', 'squared_hinge'],
                'svm__max_iter': [2000],
                'svm__tol': [1e-4, 1e-5]
            }
            
            grid_search = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                cv=5,
                scoring='accuracy',
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
        precision = precision_score(y_val, y_pred, average='weighted')
        accuracy = accuracy_score(y_val, y_pred)
        recall = recall_score(y_val, y_pred, average='weighted')
        f1 = f1_score(y_val, y_pred, average='weighted')
        
        result = [precision, accuracy, recall, f1]
        
        return result, True
        
    except Exception as e:
        print(f"Error in SVM_classifier: {str(e)}")
        return [], False
