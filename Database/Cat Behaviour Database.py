import sqlite3

DB_NAME = "cat_behaviour_database.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # CATS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        weight REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # LITTER EVENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS litter_box_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id INTEGER NOT NULL,
        enter_time TEXT,
        exit_time TEXT,
        duration_seconds INTEGER,
        visit_type TEXT,
        is_abnormal INTEGER DEFAULT 0,
        FOREIGN KEY (cat_id) REFERENCES cats(id)
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

    print("Database created successfully.")

if __name__ == "__main__":
    create_database()

    # First push