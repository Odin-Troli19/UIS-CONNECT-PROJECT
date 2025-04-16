import sqlite3

# Path to your SQLite DB
conn = sqlite3.connect("app/uis_connect.db")

with open("database/sample_data.sql", "r") as f:
    sql_script = f.read()

conn.executescript(sql_script)
conn.commit()
conn.close()

print("Sample data loaded into uis_connect.db ✅")
