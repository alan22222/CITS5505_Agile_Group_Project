import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, silhouette_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime
import json

def kmeans_function(clean_content, type):
    result = {
        'model_name': 'KMeans',
        'MSE': None,
        'precision': None
    }
    flag = False
    
    try:
        if isinstance(clean_content, pd.DataFrame):
            data = clean_content
        else:
            raise TypeError("The input data should be a pandas.DataFrame variable")
            
        # Standardize the data
        scaler = StandardScaler()
        X = scaler.fit_transform(data)
        
        # Split data into training and validation sets (80/20)
        X_train, X_val = train_test_split(X, test_size=0.2, random_state=42)
        
        # Define parameter grids based on type
        if type == "Fast":
            param_grid = {
                'n_clusters': [3, 5, 7, 9, 11]
            }
            grid_search = False
        elif type == "Balance":
            param_grid = {
                'n_clusters': np.linspace(1, 20, num=20, dtype=np.int32).tolist(),
                'init': ['k-means++', 'random'],
                'n_init': np.linspace(5, 30, num=25, dtype=np.int32).tolist(),
                'max_iter': [100, 300, 500],
                'tol': [1e-4, 1e-5]
            }
            grid_search = True
        elif type == "High Precision":
            param_grid = {
                'n_clusters': np.linspace(1, 50, num=25, dtype=np.int32).tolist(),
                'init': ['k-means++', 'random'],
                'n_init': np.linspace(5, 50, num=45, dtype=np.int32).tolist(),
                'max_iter': np.linspace(100, 1000, num=9, dtype=np.int32).tolist(),
                'tol': [1e-5, 1e-6]
            }
            grid_search = True
        else:
            return result, flag
            
        # Create and train model
        if grid_search:
            kmeans = KMeans()
            model = GridSearchCV(kmeans, param_grid, cv=5, n_jobs=-1)
        else:
            # For Fast mode, we'll just try all n_clusters values and pick the best
            best_score = -1
            best_model = None
            for n_clusters in param_grid['n_clusters']:
                model = KMeans(n_clusters=n_clusters, n_init=10)
                model.fit(X_train)
                score = silhouette_score(X_train, model.labels_)
                if score > best_score:
                    best_score = score
                    best_model = model
            model = best_model
            
        if grid_search:
            model.fit(X_train)
            best_model = model.best_estimator_
        else:
            best_model = model
            
        # Predict on validation set
        val_labels = best_model.predict(X_val)
        
        # Calculate metrics
        inertia = best_model.inertia_
        silhouette = silhouette_score(X_val, val_labels)
        
        # Store results
        result['MSE'] = inertia
        result['precision'] = float(silhouette)
        
        # Plot radar chart
        plot_path = plot_radar_chart(X_val, val_labels, best_model.n_clusters)
        result['plot_path'] = plot_path

        flag = True
        
    except Exception as e:
        print(f"Error in kmeans_function: {str(e)}")
        flag = False
        
    return result, flag

def plot_radar_chart(X, labels, n_clusters):
    try:
        # Create directory if it doesn't exist
        os.makedirs("app/plotting/", exist_ok=True)
        
        # Calculate cluster means
        cluster_means = []
        for i in range(n_clusters):
            cluster_data = X[labels == i]
            if len(cluster_data) > 0:
                cluster_means.append(np.mean(cluster_data, axis=0))
        
        if not cluster_means:
            return
            
        # Number of features
        n_features = X.shape[1]
        
        # Create radar chart
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, polar=True)
        
        # Calculate angles for each feature
        angles = np.linspace(0, 2 * np.pi, n_features, endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        for i, means in enumerate(cluster_means):
            values = means.tolist()
            values += values[:1]  # Close the loop
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=f'Cluster {i}')
            ax.fill(angles, values, alpha=0.1)
        
        # Add labels
        ax.set_thetagrids(np.degrees(angles[:-1]), range(1, n_features+1))
        ax.set_title('Cluster Characteristics Radar Chart')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        # Save plot
        timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
        plot_path = f"./static/plotting/kmeans_radar_{timestamp}.png"
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        return plot_path
        
    except Exception as e:
        print(f"Error in plot_radar_chart: {str(e)}")
        result = str(e)
        return result, False
