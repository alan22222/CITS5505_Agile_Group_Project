import sqlite3
import os
def SharingFunction(current_user_name, target_user_name, result_id):
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'database.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user IDs
        cursor.execute("SELECT id FROM user WHERE username = ?", (current_user_name,))
        current_uid = cursor.fetchone()
        if not current_uid:
            return False
        
        cursor.execute("SELECT id FROM user WHERE username = ?", (target_user_name,))
        target_uid = cursor.fetchone()
        if not target_uid:
            return False
        
        # Insert sharing record
        cursor.execute("""
            INSERT INTO SharedFiles (current_uid, target_uid, result_id)
            VALUES (?, ?, ?)
        """, (current_uid[0], target_uid[0], result_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error sharing results: {e}")
        return False
