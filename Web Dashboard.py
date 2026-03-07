import sqlite3
import os
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def dashboard():

    conn = get_db_connection()

    # -------- LITTER --------
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


    # -------- FOOD --------
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


    # -------- WATER --------
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


    # -------- HIDING --------
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


if __name__ == "__main__":
    app.run(debug=True)