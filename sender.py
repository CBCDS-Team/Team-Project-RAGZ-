import requests
import time
import datetime
import random

BASE_URL = "http://127.0.0.1:10000/api"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

while True:
    event = random.choice(["litter", "food", "water", "hiding"])

    if event == "litter":
        data = {"user_id": 2, "duration": random.randint(30, 120), "timestamp": now()}

    elif event == "food":
        data = {"user_id": 2, "amount": random.randint(10, 50), "timestamp": now()}

    elif event == "water":
        data = {"user_id": 2, "duration": random.randint(5, 30), "timestamp": now()}

    elif event == "hiding":
        data = {"user_id": 2, "duration": random.randint(60, 300), "timestamp": now()}

    url = f"{BASE_URL}/{event}"

    try:
        r = requests.post(url, json=data)
        print(event, r.status_code)
    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)