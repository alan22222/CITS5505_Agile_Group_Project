import os
import pandas as pd
from FileValidation import FileValidation
from DataWashing import DataWashing
from LinearRegression import LinearRegressionTraining
from SVM_classifier import SVMClassifier
from K_means import kmeans_function
from ResultStoring import result_storing
from ResultRetrieving import result_retrieving
from Sharing import SharingFunction
def UnitTest():
    """
    Run unit tests for all functions.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    test_file = "./data.csv"
    all_passed = True
    
    # Test FileValidation
    print("Testing FileValidation...")
    if not os.path.exists(test_file):
        print("Test file not found")
        return False
    
    if not FileValidation(test_file):
        print("FileValidation failed on valid CSV")
        all_passed = False
    else:
        print("FileValidation passed")
    
    # Test DataWashing
    print("\nTesting DataWashing...")
    try:
        df = pd.read_csv(test_file)
        cleaned_df = DataWashing(df)
        if not isinstance(cleaned_df, pd.DataFrame):
            print("DataWashing failed - didn't return DataFrame")
            all_passed = False
        else:
            print("DataWashing passed")
    except Exception as e:
        print(f"DataWashing failed: {e}")
        all_passed = False
    
    # Test LinearRegression
    print("\nTesting LinearRegression...")
    try:
        result, flag = LinearRegression(cleaned_df, 1, "Fast")
        if not flag:
            print("LinearRegression Fast failed")
            all_passed = False
        else:
            print("LinearRegression Fast passed")
            
        result, flag = LinearRegression(cleaned_df, 1, "Balance")
        if not flag:
            print("LinearRegression Balance failed")
            all_passed = False
        else:
            print("LinearRegression Balance passed")
            
        result, flag = LinearRegression(cleaned_df, 1, "High Precision")
        if not flag:
            print("LinearRegression High Precision failed")
            all_passed = False
        else:
            print("LinearRegression High Precision passed")
    except Exception as e:
        print(f"LinearRegression failed: {e}")
        all_passed = False
    
    # Test SVM_classifier
    print("\nTesting SVM_classifier...")
    try:
        result, flag = SVM_classifier(cleaned_df, 1, "Fast")
        if not flag:
            print("SVM_classifier Fast failed")
            all_passed = False
        else:
            print("SVM_classifier Fast passed")
            
        result, flag = SVM_classifier(cleaned_df, 1, "Balance")
        if not flag:
            print("SVM_classifier Balance failed")
            all_passed = False
        else:
            print("SVM_classifier Balance passed")
            
        result, flag = SVM_classifier(cleaned_df, 1, "High Precision")
        if not flag:
            print("SVM_classifier High Precision failed")
            all_passed = False
        else:
            print("SVM_classifier High Precision passed")
    except Exception as e:
        print(f"SVM_classifier failed: {e}")
        all_passed = False
    
    # Test K_means
    print("\nTesting K_means...")
    try:
        result, flag = K_means(cleaned_df, "Fast")
        if not flag:
            print("K_means Fast failed")
            all_passed = False
        else:
            print("K_means Fast passed")
            
        result, flag = K_means(cleaned_df, "Balance")
        if not flag:
            print("K_means Balance failed")
            all_passed = False
        else:
            print("K_means Balance passed")
            
        result, flag = K_means(test_file, "High Precision")
        if not flag:
            print("K_means High Precision failed")
            all_passed = False
        else:
            print("K_means High Precision passed")
    except Exception as e:
        print(f"K_means failed: {e}")
        all_passed = False
    
    return all_passed

if __name__ == "__main__":
    test_file_path = "./wdbc.csv"
    if FileValidation(test_file_path) == False:
        print("illegal file, terminated.")
        exit(1)
    df = pd.read_csv(test_file_path)
    df = DataWashing(df)
    print(df.head(10))
    # result, flag = LinearRegressionTraining(df,1,"Balance")
    # print(flag)
    # print(result)
    # result, flag = SVMClassifier(df, 1, "Balance")
    # result, flag = kmeans_function(clean_content=df, type="High Precision")
    # print(result)
    # print(flag)
    result = {'model_name': 'KMeans', 'MSE': 3136.8833264156883, 'precision': -0.02092292210604725, 'plot_path': './static/plotting/kmeans_radar_11-14-15_01-05-2025.png'}
    #flag = result_storing(result, "testuser1")
    #print(flag)
    answer = result_retrieving("testuser1")
    print(answer)