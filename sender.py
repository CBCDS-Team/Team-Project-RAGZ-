import requests
import time
import datetime
import random

BASE_URL = "https://purrmetrics.onrender.com/api"

def current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

while True:
    try:
        # Simulate different behaviours randomly
        event_type = random.choice(["litter", "food", "water", "hiding"])

        if event_type == "litter":
            data = {
                "cat_id": 1,
                "duration": random.randint(30, 90),
                "timestamp": current_time()
            }
            endpoint = "/litter"

        elif event_type == "food":
            data = {
                "cat_id": 1,
                "amount": random.randint(10, 50),
                "timestamp": current_time()
            }
            endpoint = "/food"

        elif event_type == "water":
            data = {
                "cat_id": 1,
                "duration": random.randint(5, 30),
                "timestamp": current_time()
            }
            endpoint = "/water"

        elif event_type == "hiding":
            data = {
                "cat_id": 1,
                "duration": random.randint(60, 300),
                "timestamp": current_time()
            }
            endpoint = "/hiding"

        url = BASE_URL + endpoint

        response = requests.post(url, json=data)
        print(f"{event_type.upper()} →", response.status_code, response.text)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(10)