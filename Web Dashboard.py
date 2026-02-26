import os
import sqlite3
from flask import Flask, render_template, request

# ---------------------------
# Flask app setup
# ---------------------------
app = Flask(__name__)

# ---------------------------
# Database path (ABSOLUTE)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")

# ---------------------------
# Database connection helper
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# Dashboard route
# ---------------------------
@app.route("/")
def dashboard():
    conn = get_db_connection()

    # Get selected metric from dropdown (default = total)
    selected_metric = request.args.get("litter_metric", "total")

    if selected_metric == "total":
        litter_result = conn.execute(
            "SELECT COUNT(*) FROM litter_box_events"
        ).fetchone()[0]

    elif selected_metric == "avg_per_day":
        litter_result = conn.execute("""
            SELECT COUNT(*) * 1.0 / COUNT(DISTINCT date)
            FROM litter_box_events
        """).fetchone()[0]

    elif selected_metric == "avg_duration":
        litter_result = conn.execute("""
            SELECT AVG(duration_seconds)
            FROM litter_box_events
        """).fetchone()[0]

    else:
        litter_result = 0

    conn.close()

    # Handle empty database / NULL results
    litter_result = round(litter_result, 2) if litter_result else 0

    return render_template(
        "dashboard.html",
        litter_result=litter_result,
        selected_metric=selected_metric
    )

# ---------------------------
# Run the app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)

    #first push attempt