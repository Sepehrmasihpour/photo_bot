import sqlite3
import os


def create_database():
    db_path = "seshat_manager.db"
    table_name = "group_members"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    table_exists = cursor.fetchone()
    if not table_exists:
        cursor.execute(
            f"""
            CREATE TABLE {table_name} (
                chat_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                name TEXT NOT NULL
            )
            """
        )
        conn.commit()
    conn.close()
