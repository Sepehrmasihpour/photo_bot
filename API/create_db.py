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
                name TEXT NOT NULL,
                last_proposal_date TIMESTAMP DEFAULT NULL
                
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

    # Check and create 'votes_in_progress' table if it does not exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='votes_in_progress'"
    )
    votes_in_progress_table_exists = cursor.fetchone()  # Fetch the result of the query
    if not votes_in_progress_table_exists:
        cursor.execute(
            """
            CREATE TABLE votes_in_progress (
                id INTEGER PRIMARY KEY,
                vote_type TEXT,
                is_active INTEGER NOT NULL CHECK (is_active IN (0, 1))
            )
            """
        )
        conn.commit()  # Commit the changes to the database

        # Insert initial records into the table with is_active set to 0 (inactive)
        cursor.executemany(
            """
            INSERT INTO votes_in_progress (vote_type, is_active) VALUES (?, ?)
            """,
            [("group_photo", 0), ("add_member", 0), ("remove_member", 0)],
        )
        conn.commit()  # Commit the changes to insert the records

    conn.close()  # Close the database connection


# Example usage
create_database()
