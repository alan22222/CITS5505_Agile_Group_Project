#svm classifier.py
import os
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import current_app
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


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
        from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
        cm = confusion_matrix(y_val, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot()
        
        # Save plot
        plotting_dir = os.path.join(current_app.root_path, 'static', 'plotting')
        plotting_dir = os.path.abspath(plotting_dir)
        os.makedirs(plotting_dir, exist_ok=True)

        # Generate unique filename
        filename = f"{uuid.uuid4()}.png"
        plot_path = os.path.join(plotting_dir, filename)

        # Save the plot
        plt.savefig(plot_path)
        plt.close()

    # Save this in DB for template usage
        relative_path = f'plotting/{filename}'
        graph_path = relative_path
        
        # Prepare result
        result = {
            'model_name': 'SVMClassifier',
            'Precision_value': precision,
            'Accuracy_value': accuracy,
            'Recall_value': recall,
            'F1_score_value': f1,
            'plot_path': graph_path
        }
        
        return result, True
    
    except Exception as e:
        error_message = f"Error during SVM Classifier training: {str(e)}"
        result = error_message
        return result, False

if __name__ == "__main__":
    from flask import Flask
    file_path = "../../../tests/classifier_data.csv"
    test_df = pd.read_csv(file_path)
    app = Flask(__name__)
    with app.app_context():
        for model_type in ["Fast", "Balance", "High Precision"]:
            result, success = SVMClassifier(test_df, 1, model_type)
            print(result)
            print(success)