import sqlite3

with open("database/schema.sql", "r") as schema_file:
    schema_sql = schema_file.read()

with open("database/sample_data.sql", "r") as data_file:
    data_sql = data_file.read()

conn = sqlite3.connect("app/uis_connect.db")
conn.executescript(schema_sql)
conn.executescript(data_sql)
conn.commit()
conn.close()

print("Database initialized ✅")
