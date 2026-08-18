import time
import random
import requests


# ============================================================
# ⭐ NEW: FastAPI endpoint
# ============================================================

API_URL = "http://localhost:8000/api/readings"


# ============================================================
# ⭐ NEW: Demo scenarios
# ============================================================

scenarios = [

    {
        "name": "NORMAL",
        "temperature": 30,
        "humidity": 55
    },

    {
        "name": "CAUTION",
        "temperature": 33,
        "humidity": 65
    },

    {
        "name": "WARNING",
        "temperature": 35,
        "humidity": 70
    },

    {
        "name": "DANGER",
        "temperature": 38,
        "humidity": 80
    }
]


# ============================================================
# Send data
# ============================================================

while True:

    for scenario in scenarios:

        data = {

            "device_code": "ZONE-A",

            "temperature_c": scenario["temperature"],

            "humidity_pct": scenario["humidity"]
        }


        print("\n==========================")
        print(
            f"Scenario: {scenario['name']}"
        )
        print(
            f"Temperature: {data['temperature_c']}°C"
        )
        print(
            f"Humidity: {data['humidity_pct']}%"
        )


        try:

            response = requests.post(
                API_URL,
                json=data,
                timeout=5
            )

            print(
                "Backend:",
                response.status_code
            )

            print(
                response.json()
            )

        except requests.exceptions.RequestException as e:

            print(
                "ERROR:",
                e
            )


        time.sleep(5)