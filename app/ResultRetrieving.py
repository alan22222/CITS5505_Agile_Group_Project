import sqlite3
import json
import os

def result_retrieving(user_name:str):
    flag = False
    user_results = []
    
    try:
        # Connect to SQLite database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user_id from User table
        cursor.execute("SELECT id FROM user WHERE username = ?", (user_name,))
        user_id = cursor.fetchone()
        
        if user_id:
            user_id = user_id[0]
            
            # Get all result files for this user
            cursor.execute("""
                SELECT result_json FROM model_run 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            
            for result in results:
                try:
                    data = json.loads(result[0])
                    user_results.append(data)
                except:
                    continue
            
            flag = True
        else:
            flag = False
            
        conn.close()
        
    except Exception as e:
        print(f"Error in result_retrieving: {str(e)}")
        flag = False
        
    return flag, user_results
