import os
import pandas as pd
from FileValidation import FileValidation
from DataWashing import DataWashing
from LinearRegression import LinearRegression
from ResultStoring import ResultStoring
from ResultRetrieving import ResultRetrieving
from Sharing import Sharing
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
    # test_file_path = "./data.csv"
    # if FileValidation(test_file_path) == False:
    #     print("illegal file, terminated.")
    #     exit(1)
    # df = pd.read_csv(test_file_path)
    # df = DataWashing(df)
    # print(df.head(10))
    # result, _ = LinearRegression(clean_content=df, label_column=1,type="Balance")
    # result = {'model_name': 'LinearRegression_SGD', 'MSE_value': 0.6863352320008531, 'precision_value': 0.1678926088122995}
    # print(result)
    # ResultStoring(metrics=result, u_name="testuser1")
    # _, displayed_results = ResultRetrieving(user_name="testuser1")
    # print(type(displayed_results))
    # print(displayed_results)
    flag = Sharing(current_user_name="testuser1", target_user_name="testuser2", result_info="./analysation_result/22-05-47 29-04-2025.json")
    print(flag)
