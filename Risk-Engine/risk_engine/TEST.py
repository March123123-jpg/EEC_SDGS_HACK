"""
Test client — ยิงข้อมูล sensor จำลองเข้า Risk Engine โดยตรงผ่าน HTTP
ใช้ทดสอบว่า API ทำงานถูกต้องไหม โดยไม่ต้องเปิดเบราว์เซอร์

วิธีรัน:
1. เปิด Terminal อีกอันหนึ่ง (ตัวเดิมที่รัน uvicorn อยู่ ห้ามปิด!)
   คลิกไอคอน + ที่มุมขวาบนของ Terminal panel เพื่อเปิดแท็บใหม่
2. ใน terminal ใหม่: .venv\\Scripts\\activate
3. python test_client.py
"""

import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"


def call_api(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        print(f"❌ เชื่อมต่อเซิร์ฟเวอร์ไม่ได้: {e}")
        print("   เช็คว่า uvicorn ยังรันอยู่ใน terminal อีกอันไหม")
        raise SystemExit(1)


def print_result(label: str, reading: dict, result: dict):
    print(f"\n--- {label} ---")
    print(f"  Input : {reading['temperature_c']}°C, {reading['humidity_percent']}% RH, "
          f"workload={reading['workload']}")
    print(f"  WBGT estimated : {result['wbgt_estimated']}")
    print(f"  Risk level     : {result['risk_level']}")
    print(f"  Work/rest      : {result['work_rest_regimen']}")
    print(f"  Recommendation : {result['recommendation']}")


test_cases = [
    ("เคสปลอดภัย - โกดังเบาๆ ตอนเช้า", {
        "device_id": "test-01", "location": "warehouse-test",
        "temperature_c": 24, "humidity_percent": 50, "workload": "light",
    }),
    ("เคสเฝ้าระวัง - งานกลางแจ้งช่วงสาย", {
        "device_id": "test-02", "location": "construction-test",
        "temperature_c": 28, "humidity_percent": 60, "workload": "moderate",
    }),
    ("เคสอันตราย - โรงงานเหล็กตอนเที่ยง", {
        "device_id": "test-03", "location": "steel-plant-test",
        "temperature_c": 38, "humidity_percent": 55, "workload": "heavy",
    }),
]

print("=" * 60)
print("ทดสอบ Risk Engine API")
print("=" * 60)

for label, reading in test_cases:
    result = call_api("POST", "/api/v1/sensor-data", reading)
    print_result(label, reading, result)

print("\n" + "=" * 60)
print("ดึงสถานะล่าสุดของทุกโซนกลับมาเช็คอีกที (GET /api/v1/risk/current)")
print("=" * 60)
all_current = call_api("GET", "/api/v1/risk/current")
for item in all_current:
    print(f"  {item['location']:25s} -> {item['risk_level']:10s} "
          f"(WBGT {item['wbgt_estimated']})")

print("\n✅ ทดสอบเสร็จสิ้น — ถ้าเห็นผลลัพธ์ครบทั้ง 3 เคสด้านบน แปลว่า Risk Engine ทำงานถูกต้อง")