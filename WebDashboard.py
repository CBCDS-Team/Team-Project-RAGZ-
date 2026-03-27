import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "purrmetrics_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")


# -------- DATABASE --------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_cat_id(user_id):
    conn = get_db_connection()
    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    return cat["id"] if cat else None


# -------- TIME FORMAT --------
def format_time(seconds):
    if seconds is None:
        return "0 sec"

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds} sec"

    minutes = seconds // 60
    seconds = seconds % 60

    if minutes < 60:
        return f"{minutes} min {seconds} sec"

    hours = minutes // 60
    minutes = minutes % 60

    return f"{hours} hr {minutes} min {seconds} sec"


# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, password)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return redirect("/")

    return render_template("register.html")


# -------- LOGIN --------
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    ).fetchone()

    conn.close()

    if user:
        session["user_id"] = user["id"]
        return redirect("/home")

    return "Invalid login"


# -------- PROFILE --------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()

    if request.method == "POST":
        owner_name = request.form.get("owner_name")
        cat_name = request.form.get("cat_name")

        conn.execute("""
        INSERT OR REPLACE INTO profiles
        (user_id, owner_name, cat_name)
        VALUES (?, ?, ?)
        """,
        (session["user_id"], owner_name, cat_name)
        )

        # ✅ CREATE CAT FOR USER IF NOT EXISTS
        existing_cat = conn.execute(
            "SELECT * FROM cats WHERE user_id=?",
            (session["user_id"],)
        ).fetchone()

        if not existing_cat:
            conn.execute(
                "INSERT INTO cats (user_id, name) VALUES (?, ?)",
                (session["user_id"], cat_name)
            )

        conn.commit()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template("profile.html", profile=profile)


# -------- HOME --------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    profile = conn.execute(
        "SELECT owner_name, cat_name FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    owner_name = profile["owner_name"] if profile else "User"
    cat_name = profile["cat_name"] if profile else "your cat"

    litter_visits = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE cat_id=? AND is_reset_event=0",
        (cat_id,)
    ).fetchone()[0]

    food_total = conn.execute(
        "SELECT SUM(weight_grams) FROM food_intake WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    water_total = conn.execute(
        "SELECT SUM(duration_seconds) FROM water_intake WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    hiding_events = conn.execute(
        "SELECT COUNT(*) FROM hiding_events WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    hiding_time = conn.execute(
        "SELECT SUM(duration_seconds) FROM hiding_events WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "home.html",
        owner_name=owner_name,
        cat_name=cat_name,
        litter_visits=litter_visits or 0,
        food_total=round(food_total, 2) if food_total else 0,
        water_total=format_time(water_total),
        movement_events=hiding_events or 0,
        hiding_time=format_time(hiding_time)
    )


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)