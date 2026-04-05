import requests
import time

URL = "https://purrmetrics.onrender.com/api/sensor-data"

while True:
    data = {
        "user_id": 2,  # 👈 YOUR USER ID
        "motion": True,
        "vibration": False,
        "timestamp": "2026-04-05 16:45:00"
    }

    try:
        response = requests.post(URL, json=data)
        print(response.json())
    except Exception as e:
        print("Error:", e)

    time.sleep(10)