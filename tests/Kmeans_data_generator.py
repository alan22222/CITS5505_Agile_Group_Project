import pandas as pd
import numpy as np
from sklearn.datasets import make_blobs

# 生成5个簇的1000个样本
X, y = make_blobs(n_samples=1000, 
                 n_features=2, 
                 centers=5,
                 cluster_std=1.2,
                 random_state=42)

# 创建DataFrame
df = pd.DataFrame({
    'label': y.astype(int),
    'feature1': X[:, 0],
    'feature2': X[:, 1]
})

# 保存为CSV文件
df.to_csv('./cluster_data.csv', index=False)
