import sqlite3

def SharingFunction(current_user_name, target_user_name, result_path):
    try:
        conn = sqlite3.connect('../instance/database.db')
        cursor = conn.cursor()
        
        # Get user IDs
        cursor.execute("SELECT id FROM User WHERE username = ?", (current_user_name,))
        current_uid = cursor.fetchone()
        if not current_uid:
            return False
        
        cursor.execute("SELECT id FROM User WHERE username = ?", (target_user_name,))
        target_uid = cursor.fetchone()
        if not target_uid:
            return False
        
        # Get result ID
        cursor.execute("SELECT id FROM ModelRun WHERE graph_path = ?", (result_path,))
        result_id = cursor.fetchone()
        if not result_id:
            return False
        
        # Insert sharing record
        cursor.execute("""
            INSERT INTO SharedFiles (current_uid, target_uid, result_id)
            VALUES (?, ?, ?)
        """, (current_uid[0], target_uid[0], result_id[0]))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error sharing results: {e}")
        return False
