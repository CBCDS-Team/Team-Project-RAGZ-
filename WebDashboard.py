import sqlite3
import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import calendar
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import request, jsonify
from datetime import timedelta



app = Flask(__name__)
app.secret_key = "purrmetrics_secret"

app.permanent_session_lifetime = timedelta(days=7)
app.config["SESSION_COOKIE_HTTPONLY"] = True

if "RENDER" in os.environ:
    app.config["SESSION_COOKIE_SECURE"] = True
else:
    app.config["SESSION_COOKIE_SECURE"] = False

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "Database", "cat_behaviour_database.db")
print("DB PATH:", DB_NAME)  # 👈 ADD IT HERE


# -------- DATABASE --------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_cat_id(user_id):
    conn = get_db_connection()

    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=? ORDER BY id DESC LIMIT 1",
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
        session.permanent = True
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

        # 🔹 Check if profile exists
        existing = conn.execute(
            "SELECT * FROM profiles WHERE user_id=?",
            (session["user_id"],)
        ).fetchone()

        if existing:
            # ✅ UPDATE (safe)
            conn.execute("""
                UPDATE profiles SET
                    owner_name=?,
                    cat_name=?,
                    cat_breed=?,
                    cat_dob=?,
                    cat_sex=?,
                    cat_neutered=?,
                    medical_conditions=?,
                    allergies=?,
                    medication=?
                WHERE user_id=?
            """, (
                owner_name,
                cat_name,
                cat_breed,
                cat_dob,
                cat_sex,
                cat_neutered,
                medical_conditions,
                allergies,
                medication,
                session["user_id"]
            ))
        else:
            # ✅ INSERT (only once)
            conn.execute("""
                INSERT INTO profiles (
                    user_id, owner_name, cat_name, cat_breed, cat_dob,
                    cat_sex, cat_neutered, medical_conditions,
                    allergies, medication
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        # ✅ Create or update cat safely
        existing_cat = conn.execute(
            "SELECT id FROM cats WHERE user_id=?",
            (session["user_id"],)
        ).fetchone()

        if existing_cat:
            conn.execute(
                "UPDATE cats SET name=? WHERE user_id=?",
                (cat_name, session["user_id"])
            )
        else:
            conn.execute(
                "INSERT INTO cats (user_id, name) VALUES (?, ?)",
                (session["user_id"], cat_name)
            )
        conn.commit()
        return redirect("/home")

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

    # ✅ Safe cat_photo handling
    cat_photo = None

    if profile:
        if "cat_photo" in profile.keys():
            cat_photo = profile["cat_photo"]

    return render_template(
        "profile.html",
        profile=profile,
        email=user["email"] if user else "",
        cat_photo=cat_photo
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
def calendar_view():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])
    if not cat_id:
        return "No cat found for this user."


    # Get month from URL
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    now = datetime.now()

    if not month:
        month = now.month
    if not year:
        year = now.year

    # Handle next/prev logic
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    # Get abnormal data
    dates = conn.execute("""
        SELECT date, duration_seconds
        FROM litter_box_events
        WHERE cat_id=? AND strftime('%m', date)=?
    """, (cat_id, f"{month:02d}")).fetchall()

    conn.close()

    # Severity mapping
    event_days = {}
    for row in dates:
        if row["date"]:
            day = int(row["date"].split("-")[2])
            duration = row["duration_seconds"] or 0

            if duration > 900:
                event_days[day] = "severe"
            elif duration > 600:
                event_days[day] = "warning"
            else:
                event_days[day] = "normal"

    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    return render_template(
        "calendar.html",
        calendar=cal,
        month=month_name,
        year=year,
        event_days=event_days,
        today=now.day,
        current_month=now.month,
        current_year=now.year,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year
    )
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

@app.route("/day/<int:day>")
def day_view(day):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    if not cat_id:
        return "No cat found."

    # Get events for that specific day
    events = conn.execute("""
        SELECT * FROM litter_box_events
        WHERE cat_id = ?
        AND date LIKE ?
    """, (cat_id, f"%-{day:02d}")).fetchall()

    conn.close()

    return render_template("day.html", day=day, events=events)




@app.route("/upload-cat", methods=["POST"])
def upload_cat():
    if "user_id" not in session:
        return redirect("/")

    try:
        file = request.files.get("cat_photo")

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            conn = get_db_connection()
            conn.execute(
                "UPDATE profiles SET cat_photo=? WHERE user_id=?",
                (filename, session["user_id"])
            )
            conn.commit()
            conn.close()

    except Exception as e:
        print("UPLOAD ERROR:", e)

    return redirect("/profile")

from Database.Nira_Demo_Data import generate_nira_demo_data

@app.route("/generate-demo")
def generate_demo():
    generate_nira_demo_data(session["user_id"])
    return "Demo data created!"


@app.route("/api/sensor-data", methods=["POST"])
def receive_sensor_data():
    try:
        data = request.get_json()

        user_id = data.get("user_id")  # VERY IMPORTANT
        motion = data.get("motion")
        vibration = data.get("vibration")
        timestamp = data.get("timestamp")

        conn = get_db_connection()

        # 🔹 Get user's cat
        cat = conn.execute(
            "SELECT id FROM cats WHERE user_id=?",
            (user_id,)
        ).fetchone()

        if not cat:
            return jsonify({"error": "No cat found"}), 400

        cat_id = cat["id"]

        # 🔹 Example: store as hiding event (you can change later)
        conn.execute("""
            INSERT INTO hiding_events (cat_id, timestamp, duration_seconds, location)
            VALUES (?, ?, ?, ?)
        """, (
            cat_id,
            timestamp,
            30 if motion else 0,
            "sensor"
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("API ERROR:", e)
        return jsonify({"error": "failed"}), 500


@app.route("/api/litter", methods=["POST"])
def add_litter():
    data = request.get_json()
    user_id = data.get("user_id")
    duration = data.get("duration")
    timestamp = data.get("timestamp")

    conn = get_db_connection()

    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if not cat:
        return jsonify({"error": "No cat found"}), 400

    conn.execute("""
        INSERT INTO litter_box_events (cat_id, date, duration_seconds)
        VALUES (?, ?, ?)
    """, (
        cat["id"],
        timestamp.split(" ")[0],
        duration
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "litter added"})


@app.route("/reset-litter", methods=["POST"])
def reset_litter():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    conn.execute("""
        INSERT INTO litter_box_events 
        (cat_id, date, duration_seconds, is_reset_event)
        VALUES (?, date('now'), 0, 1)
    """, (cat_id,))

    conn.commit()
    conn.close()

    return redirect("/sensors")


@app.route("/api/food", methods=["POST"])
def add_food():
    data = request.get_json()

    user_id = data.get("user_id")
    amount = data.get("amount")
    timestamp = data.get("timestamp")

    conn = get_db_connection()

    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if not cat:
        return jsonify({"error": "No cat found"}), 400

    conn.execute("""
        INSERT INTO food_intake (cat_id, timestamp, weight_grams)
        VALUES (?, ?, ?)
    """, (cat["id"], timestamp, amount))

    conn.commit()
    conn.close()

    return jsonify({"status": "food added"})


@app.route("/reset-food", methods=["POST"])
def reset_food():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    conn.execute("""
        INSERT INTO food_intake (cat_id, timestamp, weight_grams)
        VALUES (?, datetime('now'), 0)
    """, (cat_id,))

    conn.commit()
    conn.close()

    return redirect("/sensors")


@app.route("/api/water", methods=["POST"])
def add_water():
    data = request.get_json()

    user_id = data.get("user_id")
    duration = data.get("duration")
    timestamp = data.get("timestamp")

    conn = get_db_connection()

    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if not cat:
        return jsonify({"error": "No cat found"}), 400

    conn.execute("""
        INSERT INTO water_intake (cat_id, timestamp, duration_seconds)
        VALUES (?, ?, ?)
    """, (cat["id"], timestamp, duration))

    conn.commit()
    conn.close()

    return jsonify({"status": "water added"})

@app.route("/reset-water", methods=["POST"])
def reset_water():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cat_id = get_user_cat_id(session["user_id"])

    conn.execute("""
        INSERT INTO water_intake (cat_id, timestamp, duration_seconds)
        VALUES (?, datetime('now'), 0)
    """, (cat_id,))

    conn.commit()
    conn.close()

    return redirect("/sensors")


@app.route("/api/hiding", methods=["POST"])
def add_hiding():
    data = request.get_json()

    user_id = data.get("user_id")
    duration = data.get("duration")
    timestamp = data.get("timestamp")

    conn = get_db_connection()

    cat = conn.execute(
        "SELECT id FROM cats WHERE user_id=?",
        (user_id,)
    ).fetchone()

    if not cat:
        return jsonify({"error": "No cat found"}), 400

    conn.execute("""
        INSERT INTO hiding_events (cat_id, timestamp, duration_seconds, location)
        VALUES (?, ?, ?, ?)
    """, (cat["id"], timestamp, duration, "sensor"))

    conn.commit()
    conn.close()

    return jsonify({"status": "hiding added"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)