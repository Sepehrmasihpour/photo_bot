import sqlite3
import os


def create_database():
    """
    Creates the SQLite database and initializes the 'group_members' table if it does not already exist.

    This function performs the following steps:
    1. Defines the database file path and table name.
    2. Connects to the SQLite database specified by 'db_path'. If the database file does not exist, it will be created.
    3. Checks if the 'group_members' table already exists in the database.
    4. If the table does not exist, it creates the table with columns:
       - chat_id: INTEGER PRIMARY KEY
       - user_name: TEXT NOT NULL
       - name: TEXT NOT NULL
    5. Commits the changes to the database.
    6. Closes the database connection.

    This function ensures that the required table structure is present in the database
    before the application or tests attempt to use it.
    """
    db_path = "seshat_manager.db"  # Path to the SQLite database file
    table_name = "group_members"  # Name of the table to be created
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )  # Check if the table exists in the database
    table_exists = cursor.fetchone()  # Fetch the result of the query
    if not table_exists:
        # If the table does not exist, create it with the specified columns
        cursor.execute(
            f"""
            CREATE TABLE {table_name} (
                chat_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                name TEXT NOT NULL
            )
            """
        )
        conn.commit()  # Commit the changes to the database
    conn.close()  # Close the database connection
