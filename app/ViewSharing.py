import sqlite3
from typing import Tuple, List

def get_shared_results(user_name: str) -> Tuple[bool, List[str], str]:
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
    flag = False
    list_results = []
    from_who = ""
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('CITS5505')
        cursor = conn.cursor()
        
        # Get the user_id from the username
        cursor.execute("SELECT u_id FROM User_table WHERE u_name = ?", (user_name,))
        user_id_result = cursor.fetchone()
        
        if not user_id_result:
            return (False, [], "")
        
        user_id = user_id_result[0]
        
        # Get all shared results for this user
        cursor.execute("""
            SELECT sl.result_path, sl.share_from 
            FROM Share_list sl
            WHERE sl.u_id = ?
        """, (user_id,))
        
        shared_results = cursor.fetchall()
        
        if not shared_results:
            return (True, [], "")
        
        # Extract result paths
        list_results = [result[0] for result in shared_results]
        
        # Get unique sharer IDs
        sharer_ids = list(set(result[1] for result in shared_results))
        
        # Get sharer names
        placeholders = ','.join(['?'] * len(sharer_ids))
        cursor.execute(f"""
            SELECT u_name FROM User_table 
            WHERE u_id IN ({placeholders})
        """, sharer_ids)
        
        sharer_names = [name[0] for name in cursor.fetchall()]
        from_who = ", ".join(sharer_names)
        
        flag = True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flag = False
    except Exception as e:
        print(f"Error: {e}")
        flag = False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return (flag, list_results, from_who)
