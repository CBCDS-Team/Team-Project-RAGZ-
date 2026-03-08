import csv
import sqlite3

DB_NAME = "cat_behaviour_database.db"

def connect():
    return sqlite3.connect(DB_NAME)

def generate_full_report(cat_id):
    conn = connect()
    cursor = conn.cursor()

    # LITTER
    cursor.execute("SELECT COUNT(*), AVG(duration_seconds), SUM(is_abnormal) FROM litter_events WHERE cat_id = ?", (cat_id,))
    litter_total, litter_avg, litter_abnormal = cursor.fetchone()

    # FOOD
    cursor.execute("SELECT COUNT(*), SUM(weight_grams) FROM food_intake WHERE cat_id = ?", (cat_id,))
    food_total, food_sum = cursor.fetchone()

    # WATER
    cursor.execute("SELECT COUNT(*), SUM(duration_seconds) FROM water_intake WHERE cat_id = ?", (cat_id,))
    water_total, water_sum = cursor.fetchone()

    # HIDING
    cursor.execute("SELECT COUNT(*), AVG(duration_seconds) FROM hiding_events WHERE cat_id = ?", (cat_id,))
    hiding_total, hiding_avg = cursor.fetchone()

    conn.close()

    print("\n========== FULL BEHAVIOUR REPORT ==========")
    print("Cat: Diesel\n")

    print("LITTER")
    print(f"Total Visits: {litter_total}")
    print(f"Average Duration: {round(litter_avg,2) if litter_avg else 0}")
    print(f"Abnormal Visits: {litter_abnormal}")

    print("\nFOOD")
    print(f"Feeding Events: {food_total}")
    print(f"Total Food Consumed: {round(food_sum,2) if food_sum else 0}g")

    print("\nWATER")
    print(f"Drinking Events: {water_total}")
    print(f"Total Drinking Time: {water_sum if water_sum else 0}s")

    print("\nHIDING")
    print(f"Hiding Events: {hiding_total}")
    print(f"Average Hiding Duration: {round(hiding_avg,2) if hiding_avg else 0}s")

    print("\n========== HEALTH WARNINGS ==========")

    if litter_abnormal and litter_abnormal > 3:
        print("⚠ Frequent abnormal litter behaviour detected.")

    if food_sum and food_sum < 100:
        print("⚠ Low food intake detected.")

    if water_sum and water_sum > 800:
        print("⚠ Excessive water consumption detected.")

    if hiding_avg and hiding_avg > 800:
        print("⚠ Extended hiding behaviour observed.")

    print("=====================================\n")

    # CSV EXPORT
    with open("diesel_report.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Litter Visits", litter_total])
        writer.writerow(["Average Litter Duration", litter_avg])
        writer.writerow(["Abnormal Litter Visits", litter_abnormal])
        writer.writerow(["Total Food (g)", food_sum])
        writer.writerow(["Total Water (s)", water_sum])
        writer.writerow(["Average Hiding (s)", hiding_avg])

    print("CSV report exported as diesel_report.csv")

if __name__ == "__main__":
    generate_full_report(1)