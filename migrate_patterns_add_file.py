import sqlite3

conn = sqlite3.connect("yarnstash.db")

try:
    conn.execute("""
    ALTER TABLE patterns
    ADD COLUMN file_name TEXT
    """)
    print("file_name column added.")
except Exception as e:
    print("Migration skipped:", e)

conn.commit()
conn.close()