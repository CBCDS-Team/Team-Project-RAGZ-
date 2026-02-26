import sqlite3

connection = sqlite3.connect("cat_behaviour_database.db")
cursor = connection.cursor()

# Litter box usage (Load cells)
cursor.execute("""
CREATE TABLE IF NOT EXISTS litter_box_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_time TEXT,
    exit_time TEXT,
    duration_seconds INTEGER,
    date TEXT
)
""")

# Food intake (load cell)
cursor.execute("""
CREATE TABLE IF NOT EXISTS food_intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    weight_grams REAL,
    note TEXT
)
""")

# Water intake (motion-sensor)
cursor.execute("""
CREATE TABLE IF NOT EXISTS water_intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    duration_seconds INTEGER
)
""")

# Hiding behaviour (motion-sensor)
cursor.execute("""
CREATE TABLE IF NOT EXISTS hiding_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    duration_seconds INTEGER,
    location TEXT
)
""")

connection.commit()
connection.close()

print("All tables created successfully")

#attempt 2 to commit