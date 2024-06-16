import sqlite3
import os


def create_database():
    """
    Creates the SQLite database and initializes required tables if they don't already exist.
    """
    if not os.path.exists("seshat_manager.db"):
        conn = sqlite3.connect("seshat_manager.db")
        cursor = conn.cursor()

        # Create your tables here
        cursor.execute(
            """
        CREATE TABLE group_members (
            chat_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            name TEXT NOT NULL,
        )
        """
        )
        # Add other table creation statements if needed

        conn.commit()
        conn.close()
        print("Database created successfully")
    else:
        print("Database already exists")


if __name__ == "__main__":
    create_database()
