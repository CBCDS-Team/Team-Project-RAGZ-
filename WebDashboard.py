import sqlite3
import os
from datetime import datetime
from typing import Any

from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "purrmetrics_secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

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

# -------- REGISTER PAGE --------
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


# -------- LOGIN PAGE --------
@app.route("/")
@app.route("/login")
def login_page():
    return render_template("login.html")


# -------- LOGIN PROCESS --------
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
        session["email"] = user["email"]

        return redirect("/home")

    return "Invalid login"


# -------- PROFILE PAGE --------
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()

    if request.method == "POST":

        owner_name = request.form.get("owner_name")
        cat_name = request.form.get("cat_name")
        cat_dob = request.form.get("cat_dob")
        cat_sex = request.form.get("cat_sex")
        cat_neutered = request.form.get("cat_neutered")
        medical_conditions = request.form.get("medical_conditions")
        allergies = request.form.get("allergies")
        medication = request.form.get("medication")

        conn.execute("""
        INSERT OR REPLACE INTO profiles
        (user_id, owner_name, cat_name, cat_dob, cat_sex, cat_neutered, medical_conditions, allergies, medication)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            owner_name,
            cat_name,
            cat_dob,
            cat_sex,
            cat_neutered,
            medical_conditions,
            allergies,
            medication
        ))

        conn.commit()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template("profile.html", profile=profile)


# -------- HOME DASHBOARD --------
@app.route("/home")
def home():

    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()

    profile = conn.execute(
        "SELECT owner_name, cat_name FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    owner_name = profile["owner_name"] if profile else "User"
    cat_name = profile["cat_name"] if profile else "your cat"

    litter_visits = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE is_reset_event=0"
    ).fetchone()[0]

    food_total = conn.execute(
        "SELECT SUM(weight_grams) FROM food_intake"
    ).fetchone()[0]

    water_total = conn.execute(
        "SELECT SUM(duration_seconds) FROM water_intake"
    ).fetchone()[0]

    movement_events = conn.execute(
        "SELECT COUNT(*) FROM hiding_events"
    ).fetchone()[0]

    hiding_time = conn.execute(
        "SELECT SUM(duration_seconds) FROM hiding_events"
    ).fetchone()[0]

    conn.close()

    hour = datetime.now().hour

    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return render_template(
        "home.html",
        owner_name=owner_name,
        cat_name=cat_name,
        litter_visits=litter_visits or 0,
        food_total=round(food_total, 2) if food_total else 0,
        water_total=water_total or 0,
        movement_events=movement_events or 0,
        hiding_time=hiding_time or 0,
        greeting=greeting
    )


# -------- ANALYTICS DASHBOARD --------
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    chart_data = conn.execute("""
                              SELECT date, COUNT (*) as visits
                              FROM litter_box_events
                              WHERE is_reset_event = 0
                              GROUP BY date
                              ORDER BY date
                                  LIMIT 7
                              """).fetchall()

    dates = []
    visits = []

    for row in chart_data:
        day_name = datetime.strptime(row["date"], "%Y-%m-%d").strftime("%a")
        dates.append(day_name)
        visits.append(row["visits"])

    litter_result = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE is_reset_event=0"
    ).fetchone()[0]

    food_result = conn.execute(
        "SELECT COUNT(*) FROM food_intake"
    ).fetchone()[0]

    water_result = conn.execute(
        "SELECT COUNT(*) FROM water_intake"
    ).fetchone()[0]

    hiding_result = conn.execute(
        "SELECT COUNT(*) FROM hiding_events"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        litter_result=litter_result or 0,
        food_result=food_result or 0,
        water_result=water_result or 0,
        hiding_result=hiding_result or 0,
        dates=dates,
        visits=visits
    )


# -------- ABOUT --------
@app.route("/about")
def about():
    return render_template("about.html")


# -------- ALERTS --------
@app.route("/alerts")
def alerts():

    conn = get_db_connection()

    abnormal_litter = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE duration_seconds > 600"
    ).fetchone()[0]

    long_hiding = conn.execute(
        "SELECT COUNT(*) FROM hiding_events WHERE duration_seconds > 900"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "alerts.html",
        abnormal_litter=abnormal_litter or 0,
        long_hiding=long_hiding or 0
    )


# -------- SENSORS --------
@app.route("/sensors")
def sensors():

    conn = get_db_connection()

    litter_events = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE is_reset_event=0"
    ).fetchone()[0]

    food_events = conn.execute(
        "SELECT COUNT(*) FROM food_intake"
    ).fetchone()[0]

    water_events = conn.execute(
        "SELECT COUNT(*) FROM water_intake"
    ).fetchone()[0]

    hiding_events = conn.execute(
        "SELECT COUNT(*) FROM hiding_events"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "sensors.html",
        litter_events=litter_events,
        food_events=food_events,
        water_events=water_events,
        hiding_events=hiding_events
    )


# -------- CALENDAR --------
@app.route("/calendar")
def calendar():

    conn = get_db_connection()

    dates = conn.execute(
        "SELECT DISTINCT date FROM litter_box_events WHERE is_abnormal = 1").fetchall()

    conn.close()

    event_days = [row["date"] for row in dates]

    return render_template(
        "calendar.html",
        event_days=event_days
    )


# -------- RESET --------
@app.route("/reset-litter")
def reset_litter():

    conn = get_db_connection()

    conn.execute("""
        UPDATE litter_box_events
        SET is_reset_event = 1
        WHERE is_reset_event = 0
    """)

    conn.commit()
    conn.close()

    return redirect("/sensors")


# -------- DETAILED ANALYTICS --------
@app.route("/detailed-analytics")
def detailed_analytics():

    conn = get_db_connection()

    litter_avg = conn.execute(
        "SELECT AVG(duration_seconds) FROM litter_box_events WHERE is_reset_event = 0"
    ).fetchone()[0]

    hiding_avg = conn.execute(
        "SELECT AVG(duration_seconds) FROM hiding_events"
    ).fetchone()[0]

    food_total = conn.execute(
        "SELECT SUM(weight_grams) FROM food_intake"
    ).fetchone()[0]

    water_total = conn.execute(
        "SELECT SUM(duration_seconds) FROM water_intake"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "detailed_analytics.html",
        litter_avg=litter_avg or 0,
        hiding_avg=hiding_avg or 0,
        food_total=food_total or 0,
        water_total=water_total or 0
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

if __name__ == "__main__":
    app.run()