import sqlite3
import random
from datetime import datetime, timedelta



DB_NAME = "cat_behaviour_database.db"

def generate_demo_data():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM litter_box_events")
    cursor.execute("DELETE FROM food_intake")
    cursor.execute("DELETE FROM water_intake")
    cursor.execute("DELETE FROM hiding_events")

    # Create Nira if she doesn't exist
    cursor.execute("SELECT id FROM cats WHERE name = ?", ("Nira",))
    cat = cursor.fetchone()

    if cat:
        cat_id = cat[0]
    else:
        cursor.execute("""
        INSERT INTO cats (name, weight)
        VALUES (?, ?)
        """, ("Nira", 4.2))
        cat_id = cursor.lastrowid

    print("Using cat_id:", cat_id)

    # Generate 30 days of data
    for i in range(30):

        day = datetime.now() - timedelta(days=i)
        date = day.strftime("%Y-%m-%d")

        # -------------------
        # LITTER BOX VISITS
        # -------------------

        visits = random.randint(3,5)

        for v in range(visits):

            duration = random.randint(50,120)

            cursor.execute("""
            INSERT INTO litter_box_events
            (cat_id, enter_time, exit_time, duration_seconds, visit_type, is_abnormal)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                cat_id,
                date + " 10:00",
                date + " 10:02",
                duration,
                "urination",
                1 if duration > 100 else 0
            ))

        # -------------------
        # FOOD INTAKE
        # -------------------

        meals = random.randint(2,3)

        for m in range(meals):

            weight = random.randint(30,55)

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
        # WATER DRINKING
        # -------------------

        drinks = random.randint(3,6)

        for d in range(drinks):

            duration = random.randint(10,35)

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
        # HIDING EVENTS
        # -------------------

        hiding_duration = random.randint(200,900)

        cursor.execute("""
        INSERT INTO hiding_events
        (cat_id, timestamp, duration_seconds, location)
        VALUES (?, ?, ?, ?)
        """, (
            cat_id,
            date + " 15:00",
            hiding_duration,
            random.choice(["under bed","closet","sofa"])
        ))

    conn.commit()
    conn.close()

    print("30 days of demo data created successfully.")

if __name__ == "__main__":
    generate_demo_data()