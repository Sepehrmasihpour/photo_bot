from create_db import create_database
import sqlite3
from typing import Optional, Dict


def get_db_connection() -> sqlite3.Connection:
    """
    Establishes and returns a connection to the 'seshat_manager.db' SQLite database.
    The row_factory attribute is set to sqlite3.Row to allow dictionary-style access to row data.
    """
    create_database()  # Ensure the database exists by calling create_database function
    conn = sqlite3.connect("seshat_manager.db")  # Connect to the SQLite database
    conn.row_factory = (
        sqlite3.Row
    )  # Set the row_factory to sqlite3.Row for dictionary-style access
    return conn  # Return the database connection object


def get_member_info(chat_id: int) -> Optional[Dict[str, str]]:
    """
    Retrieves member information from the database based on chat_id.
    Returns a dictionary with member info if found, otherwise None.
    """
    try:
        with get_db_connection() as conn:  # Open a database connection using a context manager
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute(
                "SELECT name, user_name, last_proposal_date FROM group_members WHERE chat_id = ?",
                (chat_id,),  # Execute SQL query to fetch member info based on chat_id
            )
            row = cursor.fetchone()  # Fetch one result

        if row:
            result = {
                "name": row["name"],
                "user_name": row["user_name"],
                "last_proposal_date": row["last_proposal_date"],
            }  # Convert the result to a dictionary if a row is found
        else:
            result = None  # Return None if no row is found

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print the error message if an exception occurs
        result = None  # Return None in case of error

    return result  # Return the result


def update_member_info(chat_id: int, user_name: str, name: str) -> bool:
    """
    Updates member information in the database based on chat_id.
    Returns True if the update is successful, otherwise False.
    """
    try:
        with get_db_connection() as conn:  # Open a database connection using a context manager
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute(
                """
                UPDATE group_members
                SET user_name = ?, name = ?
                WHERE chat_id = ?
                """,
                (user_name, name, chat_id),  # Execute SQL query to update member info
            )
            conn.commit()  # Commit the transaction
        return True  # Return True if the update is successful

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print the error message if an exception occurs
        return False  # Return False in case of error


def insert_member_info(chat_id: int, name: str, user_name: str) -> bool:
    """
    Inserts new member information into the database.
    Returns True if the insertion is successful, otherwise False.
    """
    try:
        with get_db_connection() as conn:  # Open a database connection using a context manager
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute(
                """
                INSERT INTO group_members (chat_id, user_name, name)
                VALUES (?, ?, ?)
                """,
                (chat_id, user_name, name),  # Execute SQL query to insert member info
            )
            conn.commit()  # Commit the transaction
        return True  # Return True if the insertion is successful

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print the error message if an exception occurs
        return False  # Return False in case of error


def delete_member_info(chat_id: int) -> bool:
    """
    Deletes member information from the database based on chat_id.
    Returns True if the deletion is successful, otherwise False.
    """
    try:
        with get_db_connection() as conn:  # Open a database connection using a context manager
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute(
                "DELETE FROM group_members WHERE chat_id = ?",
                (chat_id,),  # Execute SQL query to delete member info based on chat_id
            )
            conn.commit()  # Commit the transaction
        return True  # Return True if the deletion is successful

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print the error message if an exception occurs
        return False  # Return False in case of error


def member_count_controll(add: bool = True) -> bool:
    """
    Controls the member count in the database.
    Increments the count if add is True, otherwise decrements the count.
    Returns True if the update is successful, otherwise False.
    """
    try:
        with get_db_connection() as conn:  # Open a database connection using a context manager
            cursor = conn.cursor()  # Create a cursor object
            cursor.execute(
                "SELECT count FROM user_count WHERE id = 1"
            )  # Execute SQL query to get current count
            count_result = cursor.fetchone()  # Fetch one result
            if count_result:
                new_count = (
                    count_result["count"] + 1 if add else count_result["count"] - 1
                )  # Calculate the new count based on add flag
                cursor.execute(
                    "UPDATE user_count SET count = ? WHERE id = 1", (new_count,)
                )  # Execute SQL query to update the count
                conn.commit()  # Commit the transaction
            return True  # Return True if the update is successful

    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Print the error message if an exception occurs
        return False  # Return False in case of error


def is_vote_active(vote_type: str):
    vote_types = ["group_photo", "add_member", "remove_member"]
    input_vote_type = vote_type.lower()
    if input_vote_type not in vote_types:
        print("There is no such vote_type")
        return None
    is_active = False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_active FROM votes_in_progress WHERE vote_type = ?",
                (input_vote_type,),  # Ensure the parameter is passed as a tuple
            )
            is_active = True if cursor.fetchone()[0] == 1 else False
        return is_active
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None
