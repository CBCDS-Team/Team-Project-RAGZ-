import sqlite3
import os

DB_NAME = "cat_behaviour_database.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # PROFILES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles(
            user_id INTEGER PRIMARY KEY,
            owner_name TEXT,
            cat_name TEXT,
            cat_dob TEXT,
            cat_sex TEXT,
            cat_neutered TEXT,
            medical_conditions TEXT,
            allergies TEXT,
            medication TEXT,
            cat_photo TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # 🔥 MIGRATIONS (this is what fixes your Render bug)
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN cat_photo TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN cat_breed TEXT")
    except sqlite3.OperationalError:
        pass

    # CATS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            weight REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # LITTER
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS litter_box_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id INTEGER NOT NULL,
            date TEXT,
            enter_time TEXT,
            exit_time TEXT,
            duration_seconds INTEGER,
            visit_type TEXT,
            is_abnormal INTEGER DEFAULT 0,
            is_reset_event INTEGER DEFAULT 0,
            FOREIGN KEY(cat_id) REFERENCES cats(id)
        )
    """)

    # FOOD
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id INTEGER NOT NULL,
            timestamp TEXT,
            weight_grams REAL,
            FOREIGN KEY (cat_id) REFERENCES cats(id)
        )
    """)

    # WATER
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id INTEGER NOT NULL,
            timestamp TEXT,
            duration_seconds INTEGER,
            FOREIGN KEY (cat_id) REFERENCES cats(id)
        )
    """)

    # HIDING
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hiding_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cat_id INTEGER NOT NULL,
            timestamp TEXT,
            duration_seconds INTEGER,
            location TEXT,
            FOREIGN KEY (cat_id) REFERENCES cats(id)
        )
    """)

    conn.commit()
    conn.close()

    print("Database ready (tables + migrations applied).")


if __name__ == "__main__":
    create_database()