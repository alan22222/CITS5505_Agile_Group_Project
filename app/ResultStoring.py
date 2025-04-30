import json
import sqlite3
import os
from datetime import datetime

def get_user_id_by_name(u_name):
    """
    Query user ID from database by username.
    
    Args:
        u_name (str): Username
        
    Returns:
        int: User ID if found, None otherwise
    """
    try:
        conn = sqlite3.connect('CITS5505.db')
        cursor = conn.cursor()
        cursor.execute("SELECT u_id FROM User_table WHERE u_name = ?", (u_name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error in get_user_id_by_name: {e}")
        return None

def ResultStoring(metrics, u_name):
    """
    Store analysis results in JSON file and database.
    
    Args:
        metrics (dict): Dictionary containing analysis metrics
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get current timestamp
        current_time = datetime.now().strftime("%H-%M-%S %d-%m-%Y")
        
        # Create directory if it doesn't exist
        os.makedirs("./analysation_result", exist_ok=True)
        
        # Save to JSON file
        file_path = f"./analysation_result/{current_time}.json"
        with open(file_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        
        # Store in database
        conn = sqlite3.connect('CITS5505.db')
        cursor = conn.cursor()
        
        # Get user_id (assuming it's stored in metrics)
        user_id = get_user_id_by_name(u_name)
        if user_id is None:
            return False
        
        # Insert into Result_table
        cursor.execute(
            "INSERT INTO Result_table (u_id, result_path, date) VALUES (?, ?, ?)",
            (user_id, file_path, current_time)
        )
        # Insert into Result_table
        cursor.execute(
            "INSERT INTO Result_table (u_id, result_path, date) VALUES (?, ?, ?)",
            (user_id, file_path, current_time)
        )
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error in ResultStoring: {e}")
        return False
