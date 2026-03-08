import sqlite3
import os
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# -------- LOGIN PAGE --------
@app.route("/")
def login_page():
    return render_template("login.html")


# -------- LOGIN PROCESS --------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # demo login
    return redirect("/home")


# -------- HOME DASHBOARD --------
@app.route("/home")
def home():

    conn = get_db_connection()

    litter_visits = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events"
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

    litter_trend = "Normal"
    alert_message = "No unusual behaviour detected"

    return render_template(
        "home.html",
        litter_visits=litter_visits or 0,
        food_total=round(food_total, 2) if food_total else 0,
        water_total=water_total or 0,
        movement_events=movement_events or 0,
        hiding_time=hiding_time or 0,
        litter_trend=litter_trend,
        alert_message=alert_message
    )


# -------- ANALYTICS DASHBOARD --------
@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    # LITTER
    litter_metric = request.args.get("litter_metric", "total")

    if litter_metric == "total":
        litter_result = conn.execute(
            "SELECT COUNT(*) FROM litter_box_events"
        ).fetchone()[0]

    elif litter_metric == "avg_duration":
        litter_result = conn.execute(
            "SELECT AVG(duration_seconds) FROM litter_box_events"
        ).fetchone()[0]

    elif litter_metric == "abnormal":
        litter_result = conn.execute(
            "SELECT COUNT(*) FROM litter_box_events WHERE duration_seconds > 600"
        ).fetchone()[0]

    else:
        litter_result = 0


    # FOOD
    food_metric = request.args.get("food_metric", "total")

    if food_metric == "total":
        food_result = conn.execute(
            "SELECT COUNT(*) FROM food_intake"
        ).fetchone()[0]

    elif food_metric == "total_food":
        food_result = conn.execute(
            "SELECT SUM(weight_grams) FROM food_intake"
        ).fetchone()[0]

    elif food_metric == "avg_food":
        food_result = conn.execute(
            "SELECT AVG(weight_grams) FROM food_intake"
        ).fetchone()[0]

    else:
        food_result = 0


    # WATER
    water_metric = request.args.get("water_metric", "total")

    if water_metric == "total":
        water_result = conn.execute(
            "SELECT COUNT(*) FROM water_intake"
        ).fetchone()[0]

    elif water_metric == "total_duration":
        water_result = conn.execute(
            "SELECT SUM(duration_seconds) FROM water_intake"
        ).fetchone()[0]

    elif water_metric == "avg_duration":
        water_result = conn.execute(
            "SELECT AVG(duration_seconds) FROM water_intake"
        ).fetchone()[0]

    else:
        water_result = 0


    # HIDING
    hiding_metric = request.args.get("hiding_metric", "total")

    if hiding_metric == "total":
        hiding_result = conn.execute(
            "SELECT COUNT(*) FROM hiding_events"
        ).fetchone()[0]

    elif hiding_metric == "avg_duration":
        hiding_result = conn.execute(
            "SELECT AVG(duration_seconds) FROM hiding_events"
        ).fetchone()[0]

    elif hiding_metric == "long_hiding":
        hiding_result = conn.execute(
            "SELECT COUNT(*) FROM hiding_events WHERE duration_seconds > 900"
        ).fetchone()[0]

    else:
        hiding_result = 0


    conn.close()

    litter_result = round(litter_result, 2) if litter_result else 0
    food_result = round(food_result, 2) if food_result else 0
    water_result = round(water_result, 2) if water_result else 0
    hiding_result = round(hiding_result, 2) if hiding_result else 0


    return render_template(
        "dashboard.html",
        litter_result=litter_result,
        food_result=food_result,
        water_result=water_result,
        hiding_result=hiding_result,
        litter_metric=litter_metric,
        food_metric=food_metric,
        water_metric=water_metric,
        hiding_metric=hiding_metric
    )


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/alerts")
def alerts():

    conn = get_db_connection()

    # ---- Basic alerts ----

    abnormal_litter = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE duration_seconds > 600"
    ).fetchone()[0]

    long_hiding = conn.execute(
        "SELECT COUNT(*) FROM hiding_events WHERE duration_seconds > 900"
    ).fetchone()[0]

    food_result = conn.execute(
        "SELECT SUM(weight_grams) FROM food_intake"
    ).fetchone()[0]

    water_result = conn.execute(
        "SELECT SUM(duration_seconds) FROM water_intake"
    ).fetchone()[0]


    # ---- Behaviour trend alerts ----

    litter_visits = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events"
    ).fetchone()[0]

    hiding_total = conn.execute(
        "SELECT SUM(duration_seconds) FROM hiding_events"
    ).fetchone()[0]


    alerts_list = []

    if litter_visits > 10:
        alerts_list.append("⚠ Litter box usage unusually high")

    if hiding_total and hiding_total > 2000:
        alerts_list.append("⚠ Cat hiding more than usual")

    if food_result and food_result < 100:
        alerts_list.append("⚠ Reduced food intake detected")

    if water_result and water_result > 1500:
        alerts_list.append("⚠ Excessive water consumption")


    conn.close()

    return render_template(
        "alerts.html",
        abnormal_litter=abnormal_litter or 0,
        long_hiding=long_hiding or 0,
        food_result=food_result or 0,
        water_result=water_result or 0,
        alerts_list=alerts_list
    )

@app.route("/calendar")
def calendar():

    conn = get_db_connection()

    # get all event dates from litter box usage
    dates = conn.execute(
        "SELECT DISTINCT date FROM litter_box_events"
    ).fetchall()

    conn.close()

    event_days = [row["date"] for row in dates]

    return render_template(
        "calendar.html",
        event_days=event_days
    )


@app.route("/detailed-analytics")
def detailed_analytics():

    conn = get_db_connection()

    litter_avg = conn.execute(
        "SELECT AVG(duration_seconds) FROM litter_box_events"
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

@app.route("/profile", methods=["GET","POST"])
def profile():
    if request.method == "POST":
        owner_name = request.form.get("owner_name")
        email = request.form.get("email")
        cat_name = request.form.get("cat_name")
        cat_breed = request.form.get("cat_breed")
        cat_dob = request.form.get("cat_dob")
        cat_sex = request.form.get("cat_sex")
        cat_neutered = request.form.get("cat_neutered")
        medical_conditions = request.form.get("medical_conditions")
        allergies = request.form.get("allergies")
        medication = request.form.get("medication")

        return render_template(
            "profile.html",
            owner_name=owner_name,
            email=email,
            cat_name=cat_name,
            cat_breed=cat_breed,
            cat_dob=cat_dob,
            cat_sex=cat_sex,
            cat_neutered=cat_neutered,
            medical_conditions=medical_conditions,
            allergies=allergies,
            medication=medication
        )

    return render_template("profile.html")


@app.route("/sensors")
def sensors():

    conn = get_db_connection()

    litter_events = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events"
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


@app.route("/reset-litter")
def reset_litter():

    conn = get_db_connection()

    conn.execute("DELETE FROM litter_box_events")

    conn.commit()
    conn.close()

    return redirect("/sensors")

@app.route("/reset-food")
def reset_food():

    conn = get_db_connection()

    conn.execute("DELETE FROM food_intake")

    conn.commit()
    conn.close()

    return redirect("/sensors")


@app.route("/reset-water")
def reset_water():

    conn = get_db_connection()

    conn.execute("DELETE FROM water_intake")

    conn.commit()
    conn.close()

    return redirect("/sensors")


if __name__ == "__main__":
    app.run(debug=True)