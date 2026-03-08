import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

cur.execute("""
CREATE TABLE history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
prompt TEXT,
response TEXT
)
""")

conn.commit()

print("Banco criado com sucesso!")