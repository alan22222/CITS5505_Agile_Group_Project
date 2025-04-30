import pandas as pd
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score
from sklearn.impute import SimpleImputer

def SVM_classifier(clean_content, label_column, type):
    """
    Train an SVM classifier with different configurations.
    
    Args:
        file_csv (str): Path to CSV file
        label_column (str/int): Label column name or index
        type (str): Training type ('Fast', 'Balance', 'High Precision')
        
    Returns:
        tuple: (result_dict, flag) where result_dict contains metrics and flag indicates success
    """
    result = {
        'model_name': 'SVM_Classifier',
        'Precision_value': None,
        'Accuracy_value': None,
        'Recall_value': None,
        'F1_score_value': None
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
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('scaler', StandardScaler()),
            ('linearsvc', LinearSVC(random_state=42))
        ])
        
        if type == 'Fast':
            params = {
                'linearsvc__C': 1,
                'linearsvc__loss': 'hinge',
                'linearsvc__max_iter': 500,
                'linearsvc__tol': 1e-3
            }
            pipeline.set_params(**params)
            pipeline.fit(X_train, y_train)
            
        elif type in ['Balance', 'High Precision']:
            # Define parameter grid based on type
            if type == 'Balance':
                param_grid = {
                    'linearsvc__C': [0.1, 1, 10],
                    'linearsvc__penalty': ['l1', 'l2'],
                    'linearsvc__loss': ['hinge', 'squared_hinge'],
                    'linearsvc__max_iter': [1000],
                    'linearsvc__tol': [1e-3, 1e-4]
                }
            else:  # High Precision
                param_grid = {
                    'linearsvc__C': np.linspace(0.1, 10, num=100).tolist(),
                    'linearsvc__penalty': ['l1', 'l2'],
                    'linearsvc__loss': ['hinge', 'squared_hinge'],
                    'linearsvc__max_iter': [2000],
                    'linearsvc__tol': [1e-4, 1e-5]
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
        
        # Evaluate on validation set
        y_pred = pipeline.predict(X_val)
        result['Precision_value'] = precision_score(y_val, y_pred, average='weighted')
        result['Accuracy_value'] = accuracy_score(y_val, y_pred)
        result['Recall_value'] = recall_score(y_val, y_pred, average='weighted')
        result['F1_score_value'] = f1_score(y_val, y_pred, average='weighted')
        flag = True
        
    except Exception as e:
        print(f"Error in SVM_classifier: {e}")
        result = str(e)
        flag = False
        
    return result, flag
