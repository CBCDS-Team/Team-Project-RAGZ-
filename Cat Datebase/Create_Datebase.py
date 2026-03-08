import sqlite3

DB_NAME = "cat_behaviour_database.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # CATS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        weight REAL NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # LITTER BOX EVENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS litter_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id INTEGER NOT NULL,
        enter_time TEXT NOT NULL,
        exit_time TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        visit_type TEXT NOT NULL,
        is_abnormal INTEGER DEFAULT 0,
        FOREIGN KEY (cat_id) REFERENCES cats(id)
    )
    """)

    # FOOD INTAKE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        weight_grams REAL NOT NULL,
        FOREIGN KEY (cat_id) REFERENCES cats(id)
    )
    """)

    # WATER INTAKE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS water_intake (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        FOREIGN KEY (cat_id) REFERENCES cats(id)
    )
    """)

    # HIDING EVENTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hiding_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cat_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        location TEXT,
        FOREIGN KEY (cat_id) REFERENCES cats(id)
    )
    """)

    conn.commit()
    conn.close()

    print("Full behaviour database created successfully.")

if __name__ == "__main__":
    create_database()