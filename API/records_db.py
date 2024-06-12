import sqlite3

conn = sqlite3.connect("seshat_manager.db")

cursur = conn.cursor()

cursur.execute(
    """
CREATE TABLE IF NOT EXISTS group_members (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
)
               """
)

conn.commit()
conn.close()
