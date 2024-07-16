import sqlite3


def create_database():
    """
    Creates the SQLite database and initializes the 'group_members', 'photos', and 'user_count' tables if they do not already exist.
    """
    db_path = "seshat_manager.db"  # Path to the SQLite database file
    conn = sqlite3.connect(db_path)  # Connect to the SQLite database
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands

    # Check and create 'group_members' table if it does not exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='group_members'"
    )
    group_members_table_exists = cursor.fetchone()  # Fetch the result of the query
    if not group_members_table_exists:
        cursor.execute(
            """
            CREATE TABLE group_members (
                chat_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                name TEXT NOT NULL
            )
            """
        )
        conn.commit()  # Commit the changes to the database

    # Check and create 'photos' table if it does not exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='photos'"
    )
    photos_table_exists = cursor.fetchone()  # Fetch the result of the query
    if not photos_table_exists:
        cursor.execute(
            """
            CREATE TABLE photos (
                file_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL
            )
            """
        )
        conn.commit()  # Commit the changes to the database

    # Check and create 'user_count' table if it does not exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='user_count'"
    )
    user_count_table_exists = cursor.fetchone()  # Fetch the result of the query
    if not user_count_table_exists:
        cursor.execute(
            """
            CREATE TABLE user_count (
                id INTEGER PRIMARY KEY,
                count INTEGER NOT NULL
            )
            """
        )
        # Initialize the user_count table with an entry
        cursor.execute("INSERT INTO user_count (id, count) VALUES (1, 0)")
        conn.commit()  # Commit the changes to the database

    conn.close()  # Close the database connection


# Example usage
create_database()
