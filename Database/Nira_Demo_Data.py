import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "cat_behaviour_database.db"

def generate_nira_demo_data(user_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 🔒 Ensure Nira belongs ONLY to this user
    cursor.execute(
        "SELECT id FROM cats WHERE name=? AND user_id=?",
        ("Nira", user_id)
    )
    cat = cursor.fetchone()

    if cat:
        cat_id = cat[0]
    else:
        cursor.execute("""
        INSERT INTO cats (user_id, name, weight)
        VALUES (?, ?, ?)
        """, (user_id, "Nira", 4.2))
        cat_id = cursor.lastrowid

    print("Using cat_id:", cat_id)

    # ❗ Clear ONLY this cat’s old data
    cursor.execute("DELETE FROM litter_box_events WHERE cat_id=?", (cat_id,))
    cursor.execute("DELETE FROM food_intake WHERE cat_id=?", (cat_id,))
    cursor.execute("DELETE FROM water_intake WHERE cat_id=?", (cat_id,))
    cursor.execute("DELETE FROM hiding_events WHERE cat_id=?", (cat_id,))

    # 📅 Generate 30 days
    for i in range(30):

        day = datetime.now() - timedelta(days=i)
        date = day.strftime("%Y-%m-%d")

        # -------------------
        # 🟤 LITTER BOX
        # -------------------
        visits = random.randint(3, 5)

        for _ in range(visits):

            # 🔥 Occasionally abnormal
            if i % 6 == 0:
                duration = random.randint(650, 900)  # ALERT
            else:
                duration = random.randint(60, 180)

            cursor.execute("""
            INSERT INTO litter_box_events
            (cat_id, date, enter_time, exit_time, duration_seconds, visit_type, is_abnormal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cat_id,
                date,
                date + " 10:00",
                date + " 10:02",
                duration,
                "urination",
                1 if duration > 600 else 0
            ))

        # -------------------
        # 🍗 FOOD
        # -------------------
        meals = random.randint(2, 3)

        for _ in range(meals):
            weight = random.randint(30, 60)

            cursor.execute("""
            INSERT INTO food_intake
            (cat_id, timestamp, weight_grams)
            VALUES (?, ?, ?)
            """, (
                cat_id,
                date + " 08:00",
                weight
            ))

        # -------------------
        # 💧 WATER
        # -------------------
        drinks = random.randint(3, 6)

        for _ in range(drinks):
            duration = random.randint(10, 40)

            cursor.execute("""
            INSERT INTO water_intake
            (cat_id, timestamp, duration_seconds)
            VALUES (?, ?, ?)
            """, (
                cat_id,
                date + " 12:00",
                duration
            ))

        # -------------------
        # 🐾 HIDING
        # -------------------

        # 🔥 Force alert days
        if i % 5 == 0:
            hiding_duration = random.randint(950, 1400)  # ALERT
        else:
            hiding_duration = random.randint(200, 600)

        cursor.execute("""
        INSERT INTO hiding_events
        (cat_id, timestamp, duration_seconds, location)
        VALUES (?, ?, ?, ?)
        """, (
            cat_id,
            date + " 15:00",
            hiding_duration,
            random.choice(["under bed", "closet", "sofa"])
        ))

    conn.commit()
    conn.close()

    print("✅ 30 days of Nira demo data created!")


# 🔥 RUN THIS (replace 1 with your user_id if needed)
if __name__ == "__main__":
    generate_nira_demo_data(1)