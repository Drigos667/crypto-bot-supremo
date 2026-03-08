import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify
from groq import Groq
import os

app = Flask(__name__)
app.secret_key="cryptobot"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def db():
    return sqlite3.connect("database.db")


@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        user=request.form["username"]
        password=request.form["password"]

        conn=db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(user,password))

        data=cur.fetchone()

        if data:
            session["user"]=user
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/chat",methods=["POST"])
def chat():

    message=request.json["message"]

    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
    You are CryptoBot, a world-class software engineer.

    When asked for a project:
    - generate the full folder structure
    - generate every file
    - include explanations
    """
            }
        ]
    )

    reply=response.choices[0].message.content

    conn=db()
    cur=conn.cursor()

    cur.execute(
        "INSERT INTO history(user,prompt,response) VALUES(?,?,?)",
        (session["user"],message,reply)
    )

    conn.commit()

    return jsonify({"reply":reply})