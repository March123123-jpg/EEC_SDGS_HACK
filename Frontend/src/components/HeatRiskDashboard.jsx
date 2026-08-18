import { Flame, Droplets, AlertTriangle, X, ShieldAlert } from "lucide-react";
import { useState, useEffect } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

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
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  // const [hoveredZone, setHoveredZone] = useState(null);
  useEffect(() => {
    const ws = new WebSocket(
      "ws://localhost:8000/ws"
    );

    ws.onopen = () => {
      console.log(
        "Connected to Heat Risk WebSocket"
      );
    };
    ws.onmessage = (event) => {
      const data = JSON.parse(
        event.data
      );

      console.log(
        "Received :",
        data
      );

      const newZone = {
        zone: data.device_code,
        temperature: data.temperature_c,
        humidity: data.humidity_pct,
        risk_level:
          data.risk_level.toLowerCase(),

        risk_value:
          data.wbgt,
        
        recommendation:
          data.recommendation,

        history: []
    };

      setZones((currentZones) => {

        const existing = 
          currentZones.find(
            (z) =>
              z.zone ===
            Zone.zone
          );

          if(existing) {

            return currentZones.map(
              (z) => {
                if (
                  z.zone !== 
                  newZone.zone
                ) {
                  return z;
                }
                return {
                  ...newZone,

                  history: [
                    ...z.history,

                    {
                      time :
                        new Date()
                        .toLocaleTimeString(),
                      
                        wbgt:
                          data.wbgt
                    }
                  ].slice(-20)
                };
              }
            );
          }

          return [
            ...currentZones,
            newZone
          ];
      });
    };

    ws.onerror = (error) => {
      console.error(
        "WebSocket error:",
        error
      );
    };

    ws.onclose = () => {
      console.log(
        "WebSocket disconnected"
      );
    };

    return () => {
      ws.onclose();
    };
},[]);
  

  const alertZones = zones.filter(
    (z) => z.risk_level === "danger" || z.risk_level === "extreme"
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, padding: 32, backgroundColor: "#0F1316", minHeight: "100vh", fontFamily: "sans-serif", color: "#E1E6E8" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16 ,borderBottom: "2px solid rgba(255, 255, 255, 0.39)", paddingBottom: 16, marginBottom: 24 }}>
        <div style={{ width: 48, height: 48, borderRadius: 12, background: "linear-gradient(135deg, #E8792E 0%, #D5432B 100%)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 20px #E8792E55" }}>
          <Flame size={26} color="#FFFFFF" />
        </div>
        <div>
          <h1 style={{ color: "white", margin: 0, fontSize: 28, fontWeight: 700 }}>Heat Risk Dashboard</h1>
          <p style={{ color: "#6C7A80", margin: "4px 0 0 0", fontSize: 14 }}>EEC Industrial Zone Monitoring</p>
        </div>
      </div>

      {alertZones.length > 0 && (
        <div
          style={{
            background: "#0F1316",
            border: "1px solid #a20f0fde",
            borderRadius: 12,
            padding: "16px 20px",
            color: "white",
            boxShadow: "0 0 25px rgba(97, 21, 10, 0.84)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, fontWeight: 600, color: "#FF6B52", fontSize: 15, marginBottom: 8 }}>
            <ShieldAlert size={20} />
            <span>แจ้งเตือน: พบ {alertZones.length} โซนที่มีความเสี่ยงสูง</span>
          </div>
          {alertZones.map((z) => (
            <div key={z.zone} style={{ fontSize: 16, color: "#A8B4B8", paddingLeft: 30 }}>
              • <strong style={{ color: "#FFF" }}>{z.zone}</strong>  <span style={{ color: getRiskColor(z.risk_level) }}>{getRiskLabel(z.risk_level)}</span> ({z.risk_value} WBGT)
            </div>
          ))}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: 20,
        }}
      >
        {zones.map((zoneData) => {
          const color = getRiskColor(zoneData.risk_level);
          const isSelected = selectedZone?.zone === zoneData.zone;
          const isHovered = hoveredZone === zoneData.zone;

          return (
            <div
              key={zoneData.zone}
              onClick={() => setSelectedZone(isSelected ? null : zoneData)}
              onMouseEnter={() => setHoveredZone(zoneData.zone)}
              onMouseLeave={() => setHoveredZone(null)}
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: `1px solid ${isSelected || isHovered ? color : "rgba(255, 255, 255, 0.39)"}`,
                borderRadius: 14,
                padding: 22,
                color: "white",
                cursor: "pointer",
                transform: isHovered ? "translateY(-4px)" : "translateY(0)",
                boxShadow: isSelected || isHovered ? `0 0 30px ${color}33, inset 0 0 15px ${color}11` : "0 4px 20px rgba(0, 0, 0, 0.3)",
                transition: "all 0.25s ease",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <span style={{ fontWeight: 700, fontSize: 18, color: "white" }}>{zoneData.zone}</span>
                <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 600, color: color, letterSpacing: 1 }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: color, boxShadow: `0 0 10px ${color}` }} />
                  {zoneData.risk_level}
                </span>
              </div>

              <div style={{ display: "flex", justifyContent: "space-around", alignItems: "center", marginBottom: 20, background: "rgba(0,0,0,0.2)", padding: "12px 16px", borderRadius: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <Flame size={22} color="#E8792E" />
                  <span style={{ fontSize: 22, fontWeight: 700, color: "white" }}>{zoneData.temperature}°C</span>
                </div>
                <div style={{ width: 1, height: 24, background: "rgba(255, 255, 255, 0.1)" }} />
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <Droplets size={22} color="#3FA7A0" />
                  <span style={{ fontSize: 22, fontWeight: 700, color: "white" }}>{zoneData.humidity}%</span>
                </div>
              </div>

              <div style={{ textAlign: "center", marginBottom: 20 }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "6px 18px",
                    borderRadius: 20,
                    fontSize: 13,
                    fontWeight: 600,
                    color: color,
                    background: `${color}15`,
                    border: `1px solid ${color}40`,
                    boxShadow: `0 0 15px ${color}22`,
                  }}
                >
                  {getRiskLabel(zoneData.risk_level)} ({zoneData.risk_value})
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: 10,
                  fontSize: 13,
                  color: "#8E9DA2",
                  borderTop: "1px solid rgba(255, 255, 255, 0.06)",
                  paddingTop: 14,
                }}
              >
                <AlertTriangle size={18} color={color} style={{ flexShrink: 0, marginTop: 2 }} />
                <span>คำแนะนำ: {zoneData.recommendation}</span>
              </div>
            </div>
          );
        })}
      </div>


      {selectedZone && (
        <div style={{ background: "#212529", padding: 24, borderRadius: 14, border: `1px solid ${getRiskColor(selectedZone.risk_level)}40`, boxShadow: `0 0 35px ${getRiskColor(selectedZone.risk_level)}15` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <h2 style={{ color: "white", margin: 0, fontSize: 18, fontWeight: 600 }}>( {selectedZone.zone} )  ประวัติแนวโน้ม WBGT</h2>
            <button
              onClick={() => setSelectedZone(null)}
              style={{ background: "rgba(255,255,255,0.05)", border: "none", color: "#dee5e8", borderRadius: 8, width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}
            >
              <X size={18} />
            </button>
          </div>

          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={selectedZone.history}>
              <defs>
                <linearGradient id="colorWbgt" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={getRiskColor(selectedZone.risk_level)} stopOpacity={0.4}/>
                  <stop offset="95%" stopColor={getRiskColor(selectedZone.risk_level)} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" stroke="#6C7A80" tick={{ fill: "#8E9DA2", fontSize: 12 }} />
              <YAxis stroke="#6C7A80" tick={{ fill: "#8E9DA2", fontSize: 12 }} domain={['dataMin - 2', 'dataMax + 2']} />
              <Tooltip contentStyle={{ backgroundColor: "#0F1316", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, color: "white" }} />
              <Area type="monotone" dataKey="wbgt" stroke={getRiskColor(selectedZone.risk_level)} strokeWidth={3} fillOpacity={1} fill="url(#colorWbgt)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}