import sqlite3

conn = sqlite3.connect("yarnstash.db")

conn.execute("""
ALTER TABLE projects
ADD COLUMN required_skeins INTEGER DEFAULT 0
""")

conn.commit()
conn.close()

print("required_skeins column added.")