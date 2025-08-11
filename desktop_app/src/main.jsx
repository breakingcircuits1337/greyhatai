import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './pages/Chat';
import Scratchpad from './pages/Scratchpad';
import VoiceSettings from './pages/VoiceSettings';
import AutoTestReport from './pages/AutoTestReport';
import { ThemeProvider, useTheme } from './ThemeContext';
import MatrixBackground from './components/MatrixBackground';

function TopBar() {
  const { theme, setTheme, themes } = useTheme();
  return (
    <div className="top-bar" style={{ background: "#111", color: "#eee", padding: "0.6rem 1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontWeight: "bold", fontSize: 22, letterSpacing: 1 }}>Grey Hat AI</span>
        <div>
          <label style={{ marginRight: 8, fontSize: 14 }}>Theme:</label>
          <select
            value={theme}
            onChange={e => setTheme(e.target.value)}
            className="dark-theme"
            style={{ fontSize: 14, background: "#23272c", color: "#eee", borderRadius: 4 }}
          >
            {themes.map(t => (
              <option value={t.key} key={t.key}>{t.label}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

function AppWrapper() {
  const { theme } = useTheme();
  return (
    <>
      {theme === "matrix" && <MatrixBackground />}
      <TopBar />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/scratchpad" element={<Scratchpad />} />
          <Route path="/voice-settings" element={<VoiceSettings />} />
          <Route path="/auto-test-report" element={<AutoTestReport />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppWrapper />
    </ThemeProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);