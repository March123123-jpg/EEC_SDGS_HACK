function getRiskColor(riskLevel) {
  if (riskLevel === "safe") return "#29e869";      
  if (riskLevel === "caution") return "#E8B23D";   
  if (riskLevel === "warn") return "#E8792E";      
  if (riskLevel === "danger") return "#D5432B";   
  if (riskLevel === "extreme") return "#A62639";   
  return "#7C8A8F"; 
}

export default function HeatRiskDashboard() {
  const mockZones = [
    {
      zone: "Zone A",
      temperature: 34.2,
      humidity: 55,
      risk_level: "danger",
      risk_value: 31.4,
      recommendation: "ลดระยะเวลาทำงานต่อเนื่อง เพิ่มรอบพัก",
    },
    {
      zone: "Zone B",
      temperature: 30.5,
      humidity: 62,
      risk_level: "caution",
      risk_value: 27.8,
      recommendation: "เพิ่มความถี่ในการพักดื่มน้ำ",
    },
    {
      zone: "Zone C",
      temperature: 27.1,
      humidity: 60,
      risk_level: "safe",
      risk_value: 25.2,
      recommendation: "สามารถปฏิบัติงานได้ตามปกติ",
    },
  ];

  return (
    <div style={{ padding: 24, color: "white", background: "#14181B", minHeight: "100vh" }}>
      <h1>Heat Risk Dashboard</h1>

      {mockZones.map((zoneData) => (
        <div key={zoneData.zone} style={{ marginBottom: 20, borderBottom: "1px solid #333", paddingBottom: 12 }}>
          <h2 style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: "50%",
                background: getRiskColor(zoneData.risk_level),
                display: "inline-block",
              }}
            />
            {zoneData.zone}
          </h2>
          <p>อุณหภูมิ: {zoneData.temperature}°C</p>
          <p>ความชื้น: {zoneData.humidity}%</p>
          <p>ระดับความเสี่ยง: {zoneData.risk_level}</p>
          <p>ค่าความเสี่ยง: {zoneData.risk_value}</p>
          <p>คำแนะนำ: {zoneData.recommendation}</p>
        </div>
      ))}
    </div>
  );
}
