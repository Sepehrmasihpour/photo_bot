import sqlite3

conn = sqlite3.connect("seshat_manager.db")

cursur = conn.cursor()

cursur.execute(
    """
CREATE TABLE IF NOT EXISTS group_members (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    name TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
)
               """
)

conn.commit()
conn.close()
