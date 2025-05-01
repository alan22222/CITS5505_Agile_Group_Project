import sqlite3

def UserLoginRegister(user_name, user_pwd, query_type):
    conn = sqlite3.connect('CITS5505.db')
    cursor = conn.cursor()
    
    try:
        if query_type == "login":
            # Check if user exists
            cursor.execute("SELECT password FROM User WHERE username = ?", (user_name,))
            result = cursor.fetchone()
            if not result:
                return 1  # User doesn't exist
            if result[0] != user_pwd:
                return 2  # Wrong password
            return 0  # Success
            
        elif query_type == "register":
            # Check if user exists
            cursor.execute("SELECT username FROM User WHERE username = ?", (user_name,))
            if cursor.fetchone():
                return 3  # Duplicate username
            # Insert new user
            cursor.execute("INSERT INTO User (username, password, email) VALUES (?, ?, ?)", 
                          (user_name, user_pwd, f"{user_name}@example.com"))
            conn.commit()
            return 0  # Success
            
        elif query_type == "reset":
            # Check if user exists
            cursor.execute("SELECT id FROM User WHERE username = ?", (user_name,))
            if not cursor.fetchone():
                return 1  # User doesn't exist
            # Update password
            cursor.execute("UPDATE User SET password = ? WHERE username = ?", (user_pwd, user_name))
            conn.commit()
            return 0  # Success
            
    except Exception as e:
        print(f"Error: {e}")
        if query_type == "login":
            return 1
        elif query_type == "register":
            return 3
        elif query_type == "reset":
            return 1
    finally:
        conn.close()
