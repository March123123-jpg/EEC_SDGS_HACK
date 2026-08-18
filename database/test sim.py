import time
import random
import psycopg2
from datetime import datetime

# ---------- 1. ตั้งค่าการเชื่อมต่อฐานข้อมูล ----------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "hackathon_project",
    "user": "postgres",
    "password": "12345678",
}

# zone_id ที่มีอยู่จริงใน table zones (ต้อง insert zones ไว้ก่อนแล้ว)
ZONE_IDS = [1, 2, 3]


# ---------- 2. ฟังก์ชันคำนวณ risk ----------
def calc_risk_level(risk_value: float) -> str:
    if risk_value < 25:
        return "SAFE"
    elif risk_value < 50:
        return "CAUTION"
    elif risk_value < 75:
        return "WARNING"
    else:
        return "DANGER"


def calc_recommendation(risk_level: str) -> str:
    mapping = {
        "SAFE": "ไม่มีความเสี่ยง สามารถทำกิจกรรมกลางแจ้งได้ตามปกติ",
        "CAUTION": "ควรดื่มน้ำให้เพียงพอและพักเป็นระยะ",
        "WARNING": "ควรหลีกเลี่ยงกิจกรรมกลางแจ้งที่ใช้แรงมาก",
        "DANGER": "ควรงดกิจกรรมกลางแจ้งทันที เสี่ยงต่อโรคลมแดด",
    }
    return mapping[risk_level]


def calc_alert_message(risk_level: str, temperature: float) -> str:
    return f"ระดับความเสี่ยง {risk_level} ที่อุณหภูมิ {temperature}°C"


# ---------- 3. ฟังก์ชันจำลองค่า sensor 1 รายการ ----------
def generate_sensor_reading(zone_id: int) -> dict:
    """
    TODO: แทนที่ตรงนี้ด้วย logic การคำนวณจริงของทีม ถ้ามีสูตรเฉพาะ
    """
    return {
        "zone_id": zone_id,
        "temperature": round(random.uniform(28.0, 42.0), 2),
        "humidity": round(random.uniform(40.0, 90.0), 2),
        "timestamp": datetime.now(),
    }


# ---------- 4. insert sensor_readings แล้วคืน id ที่ได้ ----------
def insert_sensor_reading(cur, reading: dict) -> int:
    cur.execute(
        """
        INSERT INTO sensor_readings (zone_id, temperature, humidity, timestamp)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (reading["zone_id"], reading["temperature"], reading["humidity"], reading["timestamp"]),
    )
    return cur.fetchone()[0]


# ---------- 5. insert risk_records ----------
def insert_risk_record(cur, reading_id: int, temperature: float, humidity: float):
    risk_value = (temperature - 25) * 3 + (humidity - 40) * 0.8
    risk_value = max(0, min(100, risk_value))  # กันค่าติดลบหรือเกิน 100
    recommendation = calc_recommendation(risk_level)

    cur.execute(
        """
        INSERT INTO risk_records (reading_id, risk_level, risk_value, recommendation, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (reading_id, risk_level, risk_value, recommendation, datetime.now()),
    )
    return risk_level, risk_value


# ---------- 6. insert alerts (เฉพาะกรณี WARNING / DANGER) ----------
def insert_alert(cur, zone_id: int, risk_level: str, temperature: float):
    cur.execute(
        """
        INSERT INTO alerts (zone_id, risk_level, message, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (zone_id, risk_level, calc_alert_message(risk_level, temperature), "ACTIVE", datetime.now()),
    )


# ---------- 7. Main loop ----------
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    print("เชื่อมต่อฐานข้อมูลสำเร็จ กำลังเริ่ม simulator...")

    try:
        while True:
            zones_to_gen = random.sample(ZONE_IDS, k=min(3, len(ZONE_IDS)))

            with conn.cursor() as cur:
                for zone_id in zones_to_gen:
                    reading = generate_sensor_reading(zone_id)
                    reading_id = insert_sensor_reading(cur, reading)
                    risk_level, risk_value = insert_risk_record(
                        cur, reading_id, reading["temperature"], reading["humidity"]
                    )

                    if risk_level in ("WARNING", "DANGER"):
                        insert_alert(cur, zone_id, risk_level, reading["temperature"])

                    print(
                        f"[{reading['timestamp']}] zone={zone_id} "
                        f"temp={reading['temperature']} humidity={reading['humidity']} "
                        f"-> risk={risk_level} ({risk_value})"
                    )

            conn.commit()
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nหยุด simulator แล้ว")
    finally:
        conn.close()


if __name__ == "__main__":
    main()