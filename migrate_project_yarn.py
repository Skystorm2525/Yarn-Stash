import sqlite3

conn = sqlite3.connect("yarnstash.db")

conn.execute("DROP TABLE IF EXISTS project_yarn")

conn.execute("""
CREATE TABLE project_yarn (
    project_id INTEGER,
    yarn_id INTEGER,
    skeins_used INTEGER DEFAULT 1,
    PRIMARY KEY (project_id, yarn_id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (yarn_id) REFERENCES yarn(id)
)
""")

conn.commit()
conn.close()

print("project_yarn table updated.")