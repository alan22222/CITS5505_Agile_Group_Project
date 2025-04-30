import sqlite3

def Sharing(current_user_name, target_user_name, result_info):
    """
    Share analysis results between users.
    
    Args:
        current_user_name (str): User who is sharing
        target_user_name (str): User who will receive the share
        result_info (str or int): Path to the result being shared or result ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    result_path = ""
    try:
        conn = sqlite3.connect('CITS5505.db')
        cursor = conn.cursor()
        
        # Check result_info type and assign result_path
        if isinstance(result_info, str):
            result_path = result_info
        elif isinstance(result_info, int):
            cursor.execute("SELECT result_path FROM Result_table WHERE r_id=?", (result_info,))
            result = cursor.fetchone()
            if result:
                result_path = result[0]
            else:
                return False
        
        # Get user IDs
        cursor.execute("SELECT u_id FROM User_table WHERE u_name=?", (current_user_name,))
        share_from = cursor.fetchone()
        
        cursor.execute("SELECT u_id FROM User_table WHERE u_name=?", (target_user_name,))
        u_id = cursor.fetchone()
        
        if not share_from or not u_id:
            return False
        
        share_from = share_from[0]
        u_id = u_id[0]
        
        # Insert into Share_list
        cursor.execute(
            "INSERT INTO Share_list (u_id, share_from, result_path) VALUES (?, ?, ?)",
            (u_id, share_from, result_path)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in Sharing: {e}")
        return False
    finally:
        conn.close()
