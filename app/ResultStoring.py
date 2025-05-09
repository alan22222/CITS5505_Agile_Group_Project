import os
import json
from datetime import datetime
import sqlite3

def result_storing(metrics, user_name):
    flag = False
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(f"./analysation_result/{user_name}", exist_ok=True)
        
        # Generate filename with current date
        current_date = datetime.now().strftime("%H-%M-%S %d-%m-%Y")
        file_path = f"./analysation_result/{user_name}/{current_date}.json"
        
        # Write metrics to JSON file
        with open(file_path, 'w') as f:
            json.dump(metrics, f)
        
        # Connect to SQLite database
        # Get the absolute path to the database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user_id from User table
        cursor.execute("SELECT id FROM user WHERE username = ?", (user_name,))
        user_id = cursor.fetchone()
        
        if user_id:
            user_id = user_id[0]
            
            # Insert into ModelRun table
            cursor.execute("""
                INSERT INTO model_run (
                    user_id, 
                    model_type, 
                    precision_mode,
                    has_header, 
                    result_json,
                    graph_path, 
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                metrics.get('model_name', 'UnknownModel'),
                metrics.get('speed_mode', 'UnknownSpeed'),
                metrics.get('has_header', False),
                json.dumps(metrics),
                metrics.get('plot_path', "./static/plotting/default.png"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            flag = True
        else:
            flag = False
            
        conn.close()
        
    except Exception as e:
        print(f"Error in result_storing: {str(e)}")
        flag = False
        
    return flag
