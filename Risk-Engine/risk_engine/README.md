# Heat Risk Engine

ส่วน **Risk Engine** ของโปรเจกต์ Real-time Heat Risk Monitoring & Early Warning System (EEC Hackathon)

รับข้อมูล temperature/humidity จาก sensor (จริงหรือจำลอง) → ประเมิน **WBGT** → จัดระดับ **ความเสี่ยง** ตามมาตรฐาน NIOSH/ACGIH → คืนค่า **คำแนะนำ** ให้แรงงาน/หัวหน้างาน

## เปิดใน VS Code

```bash
# 1. เข้าโฟลเดอร์
cd risk_engine

# 2. สร้าง virtual environment (ครั้งแรกครั้งเดียว)
Deter relating aCSV banalis for the fifty one simulator
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. ติดตั้ง dependencies
pip install -r requirements.txt

# 4. รันเซิร์ฟเวอร์ (auto-reload ตอนแก้โค้ด)
uvicorn main:app --reload --port 8000
```

เปิด `http://localhost:8000/docs` จะได้ Swagger UI ทดสอบ endpoint ได้ทันทีโดยไม่ต้องใช้ curl

## โครงสร้างไฟล์

| ไฟล์ | หน้าที่ |
|---|---|
| `wbgt.py` | คำนวณ WBGT โดยประมาณ จาก Temperature + Humidity |
| `risk_classifier.py` | จัดระดับความเสี่ยง (Safe/Caution/Warning/Danger) ตาม NIOSH/ACGIH TLV + คำแนะนำ |
| `models.py` | Pydantic schema (request/response) |
| `store.py` | เก็บผลล่าสุด + ประวัติของแต่ละพื้นที่ (in-memory ตอนนี้ ย้ายไป PostgreSQL ทีหลังได้) |
| `simulator.py` | จำลองข้อมูล sensor 3 โซน ไว้ demo ตอนไม่มี hardware จริง |
| `main.py` | FastAPI app รวม endpoint ทั้งหมด |
| `test_risk_engine.py` | unit test — รันด้วย `pytest test_risk_engine.py -v` |

## API หลักๆ

**ทีม IoT / ESP32 ยิงข้อมูลเข้ามาที่นี่:**
```bash
curl -X POST http://localhost:8000/api/v1/sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-01",
    "location": "steel-plant-zone-a",
    "temperature_c": 36,
    "humidity_percent": 55,
    "workload": "heavy"
  }'
```
คืนค่า `wbgt_estimated`, `risk_level`, `work_rest_regimen`, `recommendation` กลับมาทันที

**ทีม Dashboard ดึงข้อมูลไปแสดงที่นี่:**
- `GET /api/v1/risk/current` — สถานะล่าสุดทุกพื้นที่ (สำหรับหน้า overview)
- `GET /api/v1/risk/current/{location}` — ของพื้นที่เดียว
- `GET /api/v1/risk/history/{location}` — ประวัติย้อนหลัง (สำหรับกราฟ)

**Demo โดยไม่มี hardware:**
```bash
curl -X POST http://localhost:8000/api/v1/simulate/start   # เริ่มจำลอง 3 โซน ทุก 5 วิ
curl -X POST http://localhost:8000/api/v1/simulate/stop    # หยุด
```

## หมายเหตุสำคัญ (บอกทีมตอน pitching ได้)

1. **WBGT เป็นค่าประมาณ** — sensor ที่มี (DHT22/SHT31) วัดได้แค่ temp/humidity ไม่มี black-globe thermometer จึงใช้สูตร approximation (Australian BoM) แทน WBGT เต็มรูปแบบ เป็น **known limitation ที่ตรงกับข้อ 6.1.1 ใน proposal** — ถ้ามีเวลาเพิ่ม globe sensor ทีหลังได้ตามข้อ 6.2.1
2. **เกณฑ์ความเสี่ยงอ้างอิง NIOSH (2016)** ที่อยู่ในบรรณานุกรมของ proposal อยู่แล้ว ไม่ได้เดาเอง
3. แยก **workload** (light/moderate/heavy) และ **acclimatized** (แรงงานปรับตัวกับความร้อนแล้วหรือยัง) เพราะมาตรฐานจริงกำหนดเกณฑ์ต่างกันตามสองตัวนี้ — ทำให้ engine แม่นยำกว่าการมี threshold เดียว
4. Store เป็น in-memory ตอนนี้เพื่อความเร็วในการ demo — ย้ายไป PostgreSQL ภายหลังแค่แก้ `store.py` ไฟล์เดียว โค้ดส่วนอื่นไม่ต้องแตะ
