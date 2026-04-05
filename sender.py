import requests
import time
import datetime

URLS = [
    "http://127.0.0.1:10000/api/sensor-data",   # local
    "https://purrmetrics.onrender.com/api/sensor-data"  # live
]

while True:
    data = {
        "user_id": 2,
        "motion": True,
        "vibration": False,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for url in URLS:
        try:
            response = requests.post(url, json=data)
            print(url, response.json())
        except Exception as e:
            print(url, "ERROR:", e)

    time.sleep(10)