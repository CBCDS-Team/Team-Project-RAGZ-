import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "cat_behaviour_database.db"

def connect():
    return sqlite3.connect(DB_NAME)

def get_or_create_diesel():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM cats WHERE name = ?", ("Diesel",))
    result = cursor.fetchone()

    if result:
        cat_id = result[0]
    else:
        cursor.execute(
            "INSERT INTO cats (name, weight) VALUES (?, ?)",
            ("Diesel", 4.5)
        )
        conn.commit()
        cat_id = cursor.lastrowid

    conn.close()
    return cat_id

# ---------------- LITTER ----------------
def simulate_litter(cat_id):
    conn = connect()
    cursor = conn.cursor()

    enter = datetime.now()
    duration = random.randint(30, 900)
    exit_time = enter + timedelta(seconds=duration)

    abnormal = 1 if duration >= 600 else 0

    cursor.execute("""
        INSERT INTO litter_events
        (cat_id, enter_time, exit_time, duration_seconds, visit_type, is_abnormal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cat_id, enter.isoformat(), exit_time.isoformat(),
          duration, "long_stay" if abnormal else "normal", abnormal))

    conn.commit()
    conn.close()

# ---------------- FOOD ----------------
def simulate_food(cat_id):
    conn = connect()
    cursor = conn.cursor()

    weight = random.uniform(5, 120)
    abnormal = 1 if weight < 20 or weight > 100 else 0

    cursor.execute("""
        INSERT INTO food_intake
        (cat_id, timestamp, weight_grams)
        VALUES (?, ?, ?)
    """, (cat_id, datetime.now().isoformat(), weight))

    conn.commit()
    conn.close()

# ---------------- WATER ----------------
def simulate_water(cat_id):
    conn = connect()
    cursor = conn.cursor()

    duration = random.randint(5, 180)
    abnormal = 1 if duration > 120 else 0

    cursor.execute("""
        INSERT INTO water_intake
        (cat_id, timestamp, duration_seconds)
        VALUES (?, ?, ?)
    """, (cat_id, datetime.now().isoformat(), duration))

    conn.commit()
    conn.close()

# ---------------- HIDING ----------------
def simulate_hiding(cat_id):
    conn = connect()
    cursor = conn.cursor()

    duration = random.randint(60, 1500)
    abnormal = 1 if duration >= 900 else 0

    cursor.execute("""
        INSERT INTO hiding_events
        (cat_id, timestamp, duration_seconds, location)
        VALUES (?, ?, ?, ?)
    """, (cat_id, datetime.now().isoformat(),
          duration, "Under Bed"))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    cat_id = get_or_create_diesel()

    for _ in range(10):
        simulate_litter(cat_id)
        simulate_food(cat_id)
        simulate_water(cat_id)
        simulate_hiding(cat_id)

    print("Full behavioural simulation completed.")