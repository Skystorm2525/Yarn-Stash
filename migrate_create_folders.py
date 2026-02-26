import sqlite3

conn = sqlite3.connect("yarnstash.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

conn.commit()
conn.close()

print("folders table ready.")