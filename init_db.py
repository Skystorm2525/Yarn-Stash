import sqlite3

conn = sqlite3.connect("yarnstash.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS yarn (
    id INTEGER PRIMARY KEY,
    brand_name TEXT NOT NULL,
    color_name TEXT NOT NULL,
    yarn_weight INTEGER,
    skeins_owned INTEGER DEFAULT 1
)
""")

conn.execute("""
INSERT INTO yarn (brand_name, color_name, yarn_weight, skeins_owned)
VALUES ('Lion Brand', 'Cherry Red', 4, 3)
""")

conn.commit()
conn.close()

print("Database created and sample yarn added.")