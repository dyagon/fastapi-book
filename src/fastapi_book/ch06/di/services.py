import sqlite3


class UserService:
    def __init__(self, db_connection: sqlite3.Connection):
        self.db_connection = db_connection

    def get_user(self, user_id: int):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        return cursor.fetchone()
    

class AuthService:
    def __init__(self, db_connection: sqlite3.Connection):
        self.db_connection = db_connection
        
    def authenticate(self, username: str, password: str):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone() is not None