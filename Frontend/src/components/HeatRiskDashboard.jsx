export default function HeatRiskDashboard() {
  const mockZone = {
    zone: "โรงหลอมเหล็ก A",
    temperature: 34.2,
    humidity: 55,
    risk_level: "danger",
    risk_value: 31.4,
    recommendation: "ลดระยะเวลาทำงานต่อเนื่อง เพิ่มรอบพัก",
  };

  return (
    <div style={{ padding: 24, color: "white", background: "#14181B", minHeight: "100vh" }}>
      <h1>Heat Risk Dashboard</h1>
      <h2>{mockZone.zone}</h2>
      <p>อุณหภูมิ: {mockZone.temperature}°C</p>
      <p>ความชื้น: {mockZone.humidity}%</p>
      <p>ระดับความเสี่ยง: {mockZone.risk_level}</p>
      <p>ค่าความเสี่ยง: {mockZone.risk_value}</p>
      <p>คำแนะนำ: {mockZone.recommendation}</p>
    </div>
  );
}
