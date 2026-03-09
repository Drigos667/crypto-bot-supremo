import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from groq import Groq
import os

app = Flask(__name__)
app.secret_key = "cryptobot"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# conexão com banco
def db():
    return sqlite3.connect("database.db")

# criar banco automaticamente
def create_db():

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        prompt TEXT,
        response TEXT
    )
    """)

    # criar admin se não existir
    cur.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            ("admin","123")
        )

    conn.commit()
    conn.close()

create_db()

# HOME
@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return redirect("/dashboard")


# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user,password)
        )

        data = cur.fetchone()

        if data:
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")


# REGISTRO
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        user = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (user,password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("chat.html")


# CHAT IA
@app.route("/chat", methods=["POST"])
def chat():

    if "user" not in session:
        return jsonify({"reply":"login required"})

    message = request.json["message"]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role":"system",
                "content":"""
You are CryptoBot, a world-class software engineer.

When asked for a project:
- generate full folder structure
- generate every file
- include explanations
- format code clearly
"""
            },
            {
                "role":"user",
                "content":message
            }
        ]
    )

    reply = response.choices[0].message.content

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO history(user,prompt,response) VALUES(?,?,?)",
        (session["user"],message,reply)
    )

    conn.commit()
    conn.close()

    return jsonify({"reply":reply})


# HISTÓRICO
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT prompt,response FROM history WHERE user=?",
        (session["user"],)
    )

    chats = cur.fetchall()

    return jsonify(chats)


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# iniciar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
