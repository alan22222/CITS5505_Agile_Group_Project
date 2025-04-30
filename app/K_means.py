import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.impute import SimpleImputer

def K_means(clean_content, type):
    """
    Perform K-means clustering with different configurations.
    
    Args:
        file_csv (str): Path to CSV file
        type (str): Training type ('Fast', 'Balance', 'High Precision')
        
    Returns:
        tuple: (result_dict, flag) where result_dict contains metrics and flag indicates success
    """
    result = {
        'model_name': 'KMeans',
        'Silhouette_score': None,
        'Calinski_Harabasz_score': None
    }
    flag = False
    
    try:
        # Read data
        df = clean_content
        X = df.values
        
        # Split data (though clustering typically uses all data)
        X_train, X_val = train_test_split(X, test_size=0.2, random_state=42)
        
        # Create pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('kmeans', KMeans(random_state=42))
        ])
        
        if type == 'Fast':
            param_grid = {
                'kmeans__n_clusters': [3, 5, 7, 9, 11]
            }
        elif type == 'Balance':
            param_grid = {
                'kmeans__n_clusters': np.linspace(1, 20, num=20).tolist(),
                'kmeans__init': ['k-means++', 'random'],
                'kmeans__n_init': np.linspace(5, 30, num=25).tolist(),
                'kmeans__max_iter': [100, 300, 500],
                'kmeans__tol': [1e-4, 1e-5]
            }
        else:  # High Precision
            param_grid = {
                'kmeans__n_clusters': np.linspace(1, 50, num=50).tolist(),
                'kmeans__init': ['k-means++', 'random'],
                'kmeans__n_init': np.linspace(5, 50, num=45).tolist(),
                'kmeans__max_iter': np.linspace(100, 1000, num=9).tolist(),
                'kmeans__tol': [1e-4, 1e-5, 1e-6]
            }
        
        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=param_grid,
            cv=5,
            scoring='silhouette',
            n_jobs=-1,
            verbose=2
        )
        grid_search.fit(X_train)
        pipeline = grid_search.best_estimator_
        
        # Evaluate on validation set
        labels = pipeline.predict(X_val)
        result['Silhouette_score'] = silhouette_score(X_val, labels)
        result['Calinski_Harabasz_score'] = calinski_harabasz_score(X_val, labels)
        flag = True
        
    except Exception as e:
        print(f"Error in K_means: {e}")
        result = str(e)
        flag = False
        
    return result, flag
