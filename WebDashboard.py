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
        email = request.form.get("email")
        cat_name = request.form.get("cat_name")
        cat_breed = request.form.get("cat_breed")
        cat_dob = request.form.get("cat_dob")
        cat_sex = request.form.get("cat_sex")
        cat_neutered = request.form.get("cat_neutered")
        medical_conditions = request.form.get("medical_conditions")
        allergies = request.form.get("allergies")
        medication = request.form.get("medication")

        # ✅ Save full profile
        conn.execute("""
        INSERT OR REPLACE INTO profiles
        (user_id, owner_name, cat_name, cat_breed, cat_dob, cat_sex, cat_neutered, medical_conditions, allergies, medication)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            owner_name,
            cat_name,
            cat_breed,
            cat_dob,
            cat_sex,
            cat_neutered,
            medical_conditions,
            allergies,
            medication
        ))

        # ✅ Update email in users table
        conn.execute("""
        UPDATE users SET email=? WHERE id=?
        """, (email, session["user_id"]))

        # ✅ ALWAYS create/update cat for this user
        conn.execute("""
        INSERT INTO cats (user_id, name)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET name=excluded.name
        """, (session["user_id"], cat_name))

        conn.commit()

    # ✅ Get profile data
    profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    # ✅ Get email separately
    user = conn.execute(
        "SELECT email FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
        "profile.html",
        profile=profile,
        email=user["email"] if user else ""
    )

# -------- HOME --------
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()

    profile = conn.execute(
        "SELECT * FROM profiles WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    # ✅ Check if profile is incomplete
    if not profile or not profile["cat_name"]:
        conn.close()
        return render_template("home.html", setup_required=True)

    # ✅ Normal flow
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    owner_name = profile["owner_name"]
    cat_name = profile["cat_name"]

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
        setup_required=False,
        owner_name=owner_name,
        cat_name=cat_name,
        litter_visits=litter_visits or 0,
        food_total=round(food_total, 2) if food_total else 0,
        water_total=format_time(water_total),
        movement_events=hiding_events or 0,
        hiding_time=format_time(hiding_time)
    )


@app.route("/about")
def about():
    if "user_id" not in session:
        return redirect("/")

    return render_template("about.html")

@app.route("/alerts")
def alerts():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    abnormal_litter = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE cat_id=? AND duration_seconds > 600",
        (cat_id,)
    ).fetchone()[0]

    long_hiding = conn.execute(
        "SELECT COUNT(*) FROM hiding_events WHERE cat_id=? AND duration_seconds > 900",
        (cat_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "alerts.html",
        abnormal_litter=abnormal_litter or 0,
        long_hiding=long_hiding or 0,
        alerts_list=[]
    )

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    # 📊 LITTER (last 7 days)
    litter_data = conn.execute("""
        SELECT date, COUNT(*) as visits
        FROM litter_box_events
        WHERE cat_id=? AND is_reset_event=0
        GROUP BY date
        ORDER BY date ASC
        LIMIT 7
    """, (cat_id,)).fetchall()

    dates = []
    visits = []

    for row in litter_data:
        if row["date"]:
            day = datetime.strptime(row["date"], "%Y-%m-%d").strftime("%a")
            dates.append(day)
            visits.append(row["visits"])

    # 📊 FOOD (last 7 entries)
    food_data = conn.execute("""
        SELECT timestamp, weight_grams
        FROM food_intake
        WHERE cat_id=?
        ORDER BY timestamp DESC
        LIMIT 7
    """, (cat_id,)).fetchall()

    food_values = [row["weight_grams"] for row in food_data][::-1]

    # 📊 WATER
    water_data = conn.execute("""
        SELECT timestamp, duration_seconds
        FROM water_intake
        WHERE cat_id=?
        ORDER BY timestamp DESC
        LIMIT 7
    """, (cat_id,)).fetchall()

    water_values = [row["duration_seconds"] for row in water_data][::-1]

    # 📊 HIDING
    hiding_data = conn.execute("""
        SELECT timestamp, duration_seconds
        FROM hiding_events
        WHERE cat_id=?
        ORDER BY timestamp DESC
        LIMIT 7
    """, (cat_id,)).fetchall()

    hiding_values = [row["duration_seconds"] for row in hiding_data][::-1]

    conn.close()

    return render_template(
        "dashboard.html",
        dates=dates,
        visits=visits,
        food_values=food_values,
        water_values=water_values,
        hiding_values=hiding_values
    )


@app.route("/calendar")
def calendar():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    dates = conn.execute(
        "SELECT DISTINCT date FROM litter_box_events WHERE cat_id=? AND is_abnormal=1",
        (cat_id,)
    ).fetchall()

    conn.close()

    event_days = []

    for row in dates:
        if row["date"] and "-" in row["date"]:
            try:
                event_days.append(row["date"].split("-")[2])
            except:
                pass

    return render_template("calendar.html", event_days=event_days)

@app.route("/sensors")
def sensors():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    litter_events = conn.execute(
        "SELECT COUNT(*) FROM litter_box_events WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    food_events = conn.execute(
        "SELECT COUNT(*) FROM food_intake WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    water_events = conn.execute(
        "SELECT COUNT(*) FROM water_intake WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    hiding_events = conn.execute(
        "SELECT COUNT(*) FROM hiding_events WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "sensors.html",
        litter_events=litter_events,
        food_events=food_events,
        water_events=water_events,
        hiding_events=hiding_events
    )


@app.route("/detailed-analytics")
def detailed_analytics():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found. Please complete profile setup."

    # 📊 Averages (existing)
    litter_avg = conn.execute(
        "SELECT AVG(duration_seconds) FROM litter_box_events WHERE cat_id=?",
        (cat_id,)
    ).fetchone()[0]

    hiding_avg = conn.execute(
        "SELECT AVG(duration_seconds) FROM hiding_events WHERE cat_id=?",
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

    # 📊 Graph data (last 7 entries)

    litter_data = conn.execute("""
        SELECT duration_seconds FROM litter_box_events
        WHERE cat_id=? ORDER BY id DESC LIMIT 7
    """, (cat_id,)).fetchall()

    litter_values = [row["duration_seconds"] for row in litter_data][::-1]

    hiding_data = conn.execute("""
        SELECT duration_seconds FROM hiding_events
        WHERE cat_id=? ORDER BY id DESC LIMIT 7
    """, (cat_id,)).fetchall()

    hiding_values = [row["duration_seconds"] for row in hiding_data][::-1]

    food_data = conn.execute("""
        SELECT weight_grams FROM food_intake
        WHERE cat_id=? ORDER BY id DESC LIMIT 7
    """, (cat_id,)).fetchall()

    food_values = [row["weight_grams"] for row in food_data][::-1]

    water_data = conn.execute("""
        SELECT duration_seconds FROM water_intake
        WHERE cat_id=? ORDER BY id DESC LIMIT 7
    """, (cat_id,)).fetchall()

    water_values = [row["duration_seconds"] for row in water_data][::-1]

    conn.close()

    return render_template(
        "detailed_analytics.html",
        litter_avg=format_time(litter_avg),
        hiding_avg=format_time(hiding_avg),
        food_total=food_total or 0,
        water_total=format_time(water_total),

        litter_values=litter_values,
        hiding_values=hiding_values,
        food_values=food_values,
        water_values=water_values
    )


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)