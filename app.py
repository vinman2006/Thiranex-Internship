from flask import Flask, render_template, request
import re
import hashlib
import sqlite3

app = Flask(__name__)

COMMON = [
    "password",
    "123456",
    "qwerty",
    "admin",
    "password123"
]


def init_db():
    conn = sqlite3.connect("passwords.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS passwords(
        id INTEGER PRIMARY KEY,
        hash TEXT
    )
    """)

    conn.close()


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def already_used(password):

    hashed = hash_password(password)

    conn = sqlite3.connect("passwords.db")

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM passwords WHERE hash=?",
        (hashed,)
    )

    result = cur.fetchone()

    conn.close()

    return result


def save(password):

    hashed = hash_password(password)

    conn = sqlite3.connect("passwords.db")

    conn.execute(
        "INSERT INTO passwords(hash) VALUES(?)",
        (hashed,)
    )

    conn.commit()

    conn.close()


def analyze(password):

    score = 0
    feedback = []

    if len(password) >= 12:
        score += 2
    else:
        feedback.append(
            "Increase length to 12+"
        )

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append(
            "Add uppercase"
        )

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append(
            "Add lowercase"
        )

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append(
            "Add numbers"
        )

    if re.search(
            r"[!@#$%^&*]",
            password):

        score += 1

    else:
        feedback.append(
            "Add symbols"
        )

    if password.lower() in COMMON:

        feedback.append(
            "Common password"
        )

        score -= 2

    if already_used(password):

        feedback.append(
            "Password reused"
        )

        score -= 2

    if score <= 2:
        strength = "Weak"

    elif score <= 5:
        strength = "Medium"

    else:
        strength = "Strong"

    suggestion = (
        password.capitalize()
        + "@2026#"
    )

    return {
        "strength": strength,
        "feedback": feedback,
        "suggestion": suggestion
    }


@app.route(
    "/",
    methods=["GET", "POST"]
)

def home():

    result = None

    if request.method == "POST":

        password = request.form["password"]

        result = analyze(password)

        save(password)

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
