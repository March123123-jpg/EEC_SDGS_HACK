import { Flame, Droplets, AlertTriangle } from "lucide-react";
import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

function getRiskColor(riskLevel) {
  if (riskLevel === "safe") return "#29e869";      
  if (riskLevel === "caution") return "#E8B23D";   
  if (riskLevel === "warn") return "#E8792E";      
  if (riskLevel === "danger") return "#D5432B";   
  if (riskLevel === "extreme") return "#A62639";   
  return "#7C8A8F"; 
}

function getRiskLabel(riskLevel) {
  if (riskLevel === "safe") return "ปกติ";
  if (riskLevel === "caution") return "เฝ้าระวัง";
  if (riskLevel === "warn") return "เตือนภัย";
  if (riskLevel === "danger") return "อันตราย";
  if (riskLevel === "extreme") return "วิกฤต";
  return riskLevel;
}


export default function HeatRiskDashboard() {
    const [selectedZone, setSelectedZone] = useState(null);
  const mockZones = [
    {
      zone: "Zone A",
      temperature: 34.2,
      humidity: 55,
      risk_level: "danger",
      risk_value: 31.4,
      recommendation: "ลดระยะเวลาทำงานต่อเนื่อง เพิ่มรอบพัก",
        history: [
        { time: "08:00", wbgt: 27.1 },
        { time: "10:00", wbgt: 29.4 },
        { time: "12:00", wbgt: 31.4 },
        { time: "14:00", wbgt: 30.8 },
      ],
    },
    {
      zone: "Zone B",
      temperature: 30.5,
      humidity: 62,
      risk_level: "caution",
      risk_value: 27.8,
      recommendation: "เพิ่มความถี่ในการพักดื่มน้ำ",
      history: [
        { time: "08:00", wbgt: 25.1 },
        { time: "10:00", wbgt: 26.8 },
        { time: "12:00", wbgt: 27.8 },
        { time: "14:00", wbgt: 27.2 },
      ],
    },
    {
      zone: "Zone C",
      temperature: 27.1,
      humidity: 60,
      risk_level: "safe",
      risk_value: 25.2,
      recommendation: "สามารถปฏิบัติงานได้ตามปกติ",
      history: [
        { time: "08:00", wbgt: 24.1 },
        { time: "10:00", wbgt: 25.8 },
        { time: "12:00", wbgt: 25.2 },
        { time: "14:00", wbgt: 24.8 },
      ],
    },
  ];

  return (
    <div style={{ padding: 32, background: "#14181B", minHeight: "100vh", fontFamily: "sans-serif" }}>
      <h1 style={{ color: "white", marginBottom: 24 }}>Heat Risk Dashboard</h1>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: 16,
        }}
      >
      {mockZones.map((zoneData) => {
        const color = getRiskColor(zoneData.risk_level);
          return (
            <div
              key={zoneData.zone}
              onClick={() => setSelectedZone(zoneData)}
              style={{
                background: "#1D2327",
                border: `1px solid ${color}55`,
                borderRadius: 8,
                padding: 20,
                color: "white",
              }}
            >
               <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <span
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: color,
                    display: "inline-block",
                  }}
                />
                <span style={{ fontWeight: 600, fontSize: 16 }}>{zoneData.zone}</span>
              </div>
             <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14 }}>
                  <Flame size={16} color="#E8792E" />
                  <span>{zoneData.temperature}°C</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14 }}>
                  <Droplets size={16} color="#3FA7A0" />
                  <span>{zoneData.humidity}%</span>
                </div>
              </div>

              <div
                style={{
                  display: "inline-block",
                  padding: "4px 10px",
                  borderRadius: 4,
                  fontSize: 12,
                  fontWeight: 600,
                  color: color,
                  background: `${color}22`,
                  marginBottom: 14,
                }}
              >
                {getRiskLabel(zoneData.risk_level)} ({zoneData.risk_value})
              </div>
              <div
                style={{
                  display: "flex",
                  gap: 8,
                  fontSize: 13,
                  color: "#C9C4B8",
                  borderTop: "1px solid #2B3237",
                  paddingTop: 12,
                }}
              >
                <AlertTriangle size={16} color={color} style={{ flexShrink: 0, marginTop: 2 }} />
                <span>{zoneData.recommendation}</span>
              </div>
            </div>
          );
        })}
      </div>
              {selectedZone && (
            <div style={{  marginTop: 32 ,background: "#1D2327", padding: 20, borderRadius: 8 }}>
                <h2 style={{ color: "white", marginBottom: 16 }}>{selectedZone.zone} - ประวัติ WBGT</h2>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={selectedZone.history}>
                        <CartesianGrid stroke="#2B3237" />
                        <XAxis dataKey="time" stroke="#C9C4B8" />
                        <YAxis stroke="#C9C4B8" />
                        <Tooltip contentStyle={{ backgroundColor: "#1D2327", border: "none", color: "white" }} />
                        <Line type="monotone" dataKey="wbgt" stroke={getRiskColor(selectedZone.risk_level)} strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        )}
    </div>
  );
}