import json
import sqlite3
import os

def ResultRetrieving(user_name):
    """
    Retrieve analysis results for a specific user.
    
    Args:
        user_name (str): Username to retrieve results for
        
    Returns:
        tuple: (flag, user_results) where flag indicates success and user_results contains the data
    """
    user_results = []
    flag = False
    
    try:
        conn = sqlite3.connect('CITS5505.db')
        cursor = conn.cursor()
        
        # Get user_id from username
        cursor.execute("SELECT u_id FROM User_table WHERE u_name=?", (user_name,))
        user_id = cursor.fetchone()
        print(f"Fetched user_id: {user_id}")
        
        if not user_id:
            print("User not found")
            return False, []
        
        user_id = user_id[0]
        
        # Get result paths for this user
        cursor.execute(
            "SELECT result_path FROM Result_table WHERE u_id=?",
            (user_id,)
        )
        result_paths = cursor.fetchall()
        print(f"Fetched result paths: {result_paths}")
        
        # Read each result file
        for path in result_paths:
            print(f"Processing path: {path[0]}")
            try:
                with open(path[0], 'r') as f:
                    data = json.load(f)
                    user_results.append(data)
            except Exception as e:
                print(f"Error reading file {path[0]}: {e}")
                continue
        
        flag = True
    except Exception as e:
        print(f"Error in ResultRetrieving: {e}")
    finally:
        conn.close()
    
    return flag, user_results
