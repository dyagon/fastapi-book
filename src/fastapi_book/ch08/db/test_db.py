import sqlite3

def get_test_db_connection():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (1, "alice", "secret"))
    cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (2, "bob", "password"))
    conn.commit()
    return conn


def main():
    conn = get_test_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Users in test DB:", users)
    conn.close()

if __name__ == "__main__":
    main()