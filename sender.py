from gpiozero import MotionSensor, Button
import requests
import datetime
import time

hiding_sensor = MotionSensor(4)
water_sensor = MotionSensor(17)
litter_sensor = Button(27)

BASE_URL = "https://purrmetrics.onrender.com/api"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

while True:

    hiding_sensor.wait_for_motion()
    print("Hiding detected")

    requests.post(f"{BASE_URL}/hiding", json={
        "user_id": 2,
        "duration": 120,
        "timestamp": now()
    })

    time.sleep(3)

    if water_sensor.motion_detected:
        print("Water activity")

        requests.post(f"{BASE_URL}/water", json={
            "user_id": 2,
            "duration": 10,
            "timestamp": now()
        })

        time.sleep(3)

    if litter_sensor.is_pressed:
        print("Litter box used")

        requests.post(f"{BASE_URL}/litter", json={
            "user_id": 2,
            "duration": 60,
            "timestamp": now()
        })

        time.sleep(3)