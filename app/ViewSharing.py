import sqlite3
from typing import Tuple, List
import os
def get_user_results_by_username(username: str):
    """
    Retrieve all result paths shared with a given user and identify the sharers.
    
    Args:
        user_name: The name of the user to query shared results for
        
    Returns:
        A tuple containing:
        - flag: True if SQL operations succeeded, False otherwise
        - list_results: List of result paths shared with the user
        - From_who: String containing names of sharers separated by commas
    """
    
    try:
        # Connect to the SQLite database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the user_id from the username
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        user_id_result = cursor.fetchone()
        
        if not user_id_result:
            return (False, [], "")
        
        user_id = user_id_result[0]
        
        # Join query to get result_json from model_run
        cursor.execute("""
            SELECT mr.result_json
            FROM SharedFiles sf
            JOIN model_run mr ON sf.result_id = mr.id
            WHERE sf.target_uid = ?
        """, (user_id,))

        results = cursor.fetchall()

        # Extract result_json content
        result_jsons = [result[0] for result in results]

        return result_jsons, True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None, False
    finally:
        if 'conn' in locals():
            conn.close()
