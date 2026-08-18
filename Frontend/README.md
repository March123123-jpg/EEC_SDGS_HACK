# Heat Risk Dashboard (Frontend)

Dashboard แสดงสถานะความเสี่ยงจากความร้อนของแรงงานในพื้นที่อุตสาหกรรม EEC
ส่วนหนึ่งของโปรเจกต์ Real-time Heat Risk Monitoring & Early Warning System

พัฒนาด้วย **React and Vite**

## Features

- แสดงอุณหภูมิ ความชื้น และระดับความเสี่ยง (Risk Level) ของแต่ละโซน
- จุดสีและป้ายบอกสถานะความเสี่ยงแบบ real-time
- แจ้งเตือนอัตโนมัติ (Alert) เมื่อพบโซนที่มีความเสี่ยงสูง
- กราฟแนวโน้ม WBGT ย้อนหลังของแต่ละโซน
- คำแนะนำการปฏิบัติงานตามระดับความเสี่ยง

## โครงสร้างโปรเจกต์
```

Frontend/
│
├── 📂 src/
│   ├── 📂 assets/
│   │
│   ├── 📂 components/
│   │   └── 📄 HeatRiskDashboard.jsx
│   │
│   ├── 🎨 App.css
│   ├── ⚛️ App.jsx
│   ├── 🎨 index.css
│   └── ⚛️ main.jsx
│
├── 📄 index.html
├── 📦 package.json
├── 📦 package-lock.json
├── ⚙️ vite.config.js
├── 🚫 .gitignore
└── 📖 README.md
```

## วิธีรัน

```bash
npm install
npm run dev
```

จากนั้นเปิด [http://localhost:5173](http://localhost:5173)

## Tech Stack

- React ไลบรารีหลักสำหรับสร้าง UI ที่มีประสิทธิภาพสูง
- Vite เครื่องมือ Build Tool ที่เร็วมาก ช่วยให้เริ่มโปรเจกต์และรีโหลดหน้าเว็บตอนพัฒนาได้ทันใจ
- Recharts ไลบรารีทำกราฟที่รองรับ Responsive และเข้ากับคอมโพเนนต์ของ React ได้อย่างลงตัว
- Lucide React ชุดไอคอนสไตล์มินิมอลที่สวยงาม โหลดเร็ว และปรับแต่งได้ง่าย