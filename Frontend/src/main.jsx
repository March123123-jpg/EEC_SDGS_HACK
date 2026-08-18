import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import HeatRiskDashboard from './components/HeatRiskDashboard' 

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <HeatRiskDashboard />
  </StrictMode>,
)
