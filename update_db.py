import sqlite3

conn = sqlite3.connect("yarnstash.db")

# Patterns table
conn.execute("""
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT
)
""")

# Projects table
conn.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    pattern_id INTEGER,
    FOREIGN KEY (pattern_id) REFERENCES patterns(id)
)
""")

# Project-Yarn link table
conn.execute("""
CREATE TABLE IF NOT EXISTS project_yarn (
    project_id INTEGER,
    yarn_id INTEGER,
    PRIMARY KEY (project_id, yarn_id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (yarn_id) REFERENCES yarn(id)
)
""")

conn.commit()
conn.close()

print("Database updated.")