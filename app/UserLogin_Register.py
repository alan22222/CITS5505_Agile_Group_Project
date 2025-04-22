import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection"""
    conn = sqlite3.connect('user_database.db')
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    """Initialize the database with required tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create User table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_table (
            u_id INTEGER PRIMARY KEY AUTOINCREMENT,
            u_name VARCHAR(255) UNIQUE NOT NULL,
            u_pwd VARCHAR(255) NOT NULL
        )
        ''')
        
        # Create Result table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Result_table (
            u_id INTEGER NOT NULL,
            r_id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_path VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (u_id) REFERENCES User_table(u_id)
        )
        ''')
        
        # Create Share_list table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Share_list (
            u_id INTEGER NOT NULL,
            share_from INTEGER NOT NULL,
            r_id INTEGER NOT NULL,
            FOREIGN KEY (u_id) REFERENCES User_table(u_id),
            FOREIGN KEY (share_from) REFERENCES User_table(u_id),
            FOREIGN KEY (r_id) REFERENCES Result_table(r_id),
            PRIMARY KEY (u_id, r_id)
        )
        ''')
        
        conn.commit()

# Initialize database when module is imported
initialize_database()

def User_login_and_register(user_name, user_pwd, query_type):
    """
    Handle user login, registration, and password reset operations.
    
    Args:
        user_name (str): User name
        user_pwd (str): User password
        query_type (str): Operation type ('login', 'register', 'reset')
        
    Returns:
        int: Status code (0=success, 1=user not found, 2=wrong password, 3=duplicate user)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if query_type == 'login':
            # Check if user exists
            cursor.execute('SELECT u_pwd FROM User_table WHERE u_name = ?', (user_name,))
            result = cursor.fetchone()
            
            if not result:
                return 1  # User not found
            
            stored_pwd = result[0]
            if stored_pwd != user_pwd:
                return 2  # Wrong password
                
            return 0  # Success
            
        elif query_type == 'register':
            # Check if user exists
            cursor.execute('SELECT u_id FROM User_table WHERE u_name = ?', (user_name,))
            if cursor.fetchone():
                return 3  # Duplicate user
                
            # Insert new user
            try:
                cursor.execute(
                    'INSERT INTO User_table (u_name, u_pwd) VALUES (?, ?)',
                    (user_name, user_pwd)
                )
                conn.commit()
                return 0  # Success
            except sqlite3.IntegrityError:
                return 3  # Duplicate user (race condition)
                
        elif query_type == 'reset':
            # Check if user exists
            cursor.execute('SELECT u_id FROM User_table WHERE u_name = ?', (user_name,))
            if not cursor.fetchone():
                return 1  # User not found
                
            # Update password
            cursor.execute(
                'UPDATE User_table SET u_pwd = ? WHERE u_name = ?',
                (user_pwd, user_name)
            )
            conn.commit()
            return 0  # Success
            
        else:
            raise ValueError("Invalid query_type. Must be 'login', 'register', or 'reset'")
