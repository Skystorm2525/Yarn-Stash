import sqlite3

conn = sqlite3.connect("yarnstash.db")

try:
    conn.execute("""
    ALTER TABLE patterns
    ADD COLUMN folder_id INTEGER
    """)
    print("folder_id column added.")
except Exception as e:
    print("Migration skipped:", e)

conn.commit()
conn.close()