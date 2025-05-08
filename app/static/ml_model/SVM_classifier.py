import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, accuracy_score, recall_score, f1_score
import matplotlib.pyplot as plt
import os
import uuid

def SVMClassifier(clean_data, label_column, type):
    try:
        if isinstance(clean_data, pd.DataFrame):
            df = clean_data
        else:
            raise TypeError("The input data should be a pandas.DataFrame variable")
        # Handle label column
        if isinstance(label_column, str):
            y = df[label_column]
            X = df.drop(label_column, axis=1)
        else:
            y = df.iloc[:, label_column]
            X = df.drop(df.columns[label_column], axis=1)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Create pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('linearsvc', LinearSVC(random_state=42))
        ])
        
        # Different parameters based on type
        if type == "Fast":
            params = {
                'linearsvc__C': 1,
                'linearsvc__loss': 'hinge',
                'linearsvc__max_iter': 500,
                'linearsvc__tol': 1e-3
            }
            pipeline.set_params(**params)
            pipeline.fit(X_train, y_train)
            
        elif type == "Balance":
            param_grid = {
                'linearsvc__C': [0.1, 1, 10],
                'linearsvc__penalty': ['l1', 'l2'],
                'linearsvc__loss': ['hinge', 'squared_hinge'],
                'linearsvc__max_iter': [1000],
                'linearsvc__tol': [1e-3, 1e-4]
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
                'linearsvc__C': np.linspace(0.1, 10, num=50).tolist(),
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
        
        # Predict and calculate metrics
        y_pred = pipeline.predict(X_val)
        precision = precision_score(y_val, y_pred, average='weighted')
        accuracy = accuracy_score(y_val, y_pred)
        recall = recall_score(y_val, y_pred, average='weighted')
        f1 = f1_score(y_val, y_pred, average='weighted')
        
        # Plotting (confusion matrix)
        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
        cm = confusion_matrix(y_val, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        
        # Save plot
        os.makedirs('app/plotting/', exist_ok=True)
        plot_path = f'app/plotting/{uuid.uuid4()}.png'
        plt.savefig(plot_path)
        plt.close()
        
        # Prepare result
        result = {
            'model_name': 'SVMClassifier',
            'Precision_value': precision,
            'Accuracy_value': accuracy,
            'Recall_value': recall,
            'F1_score_value': f1,
            'plot_path': plot_path
        }
        
        return result, True
    
    except Exception as e:
        error_message = f"Error during SVM Classifier training: {str(e)}"
        result = error_message
        return result, False
