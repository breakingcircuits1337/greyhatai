import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './pages/Chat';
import Scratchpad from './pages/Scratchpad';
import VoiceSettings from './pages/VoiceSettings';
import AutoTestReport from './pages/AutoTestReport';
import TerminalPage from './pages/Terminal';
import FileExplorer from './pages/FileExplorer';
import SessionManager from './pages/SessionManager';
import { ThemeProvider, useTheme } from './ThemeContext';
import MatrixBackground from './components/MatrixBackground';

import { useState, useEffect } from "react";

function TopBar() {
  const { theme, setTheme, themes } = useTheme();
  const [recording, setRecording] = useState(false);

  // Cross-platform detection for Ctrl+Shift+G
  useEffect(() => {
    function onKeyDown(e) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.code === "KeyG" || e.key === "g" || e.key === "G")) {
        // Only trigger if not already recording
        if (!recording) {
          fetch("http://localhost:8000/voice/start", { method: "POST" });
          setRecording(true);
        }
      }
    }
    function onKeyUp(e) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.code === "KeyG" || e.key === "g" || e.key === "G")) {
        // Only stop if currently recording
        if (recording) {
          fetch("http://localhost:8000/voice/stop", { method: "POST" });
          setRecording(false);
        }
      }
    }
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
    // eslint-disable-next-line
  }, [recording]);

  return (
    <div className="top-bar" style={{ background: "#111", color: "#eee", padding: "0.6rem 1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontWeight: "bold", fontSize: 22, letterSpacing: 1 }}>Grey Hat AI</span>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <a href="/terminal" style={{ color: "#2ecc40", textDecoration: "none", marginRight: 10, fontWeight: 500 }}>Terminal</a>
          <a href="/explorer" style={{ color: "#39f369", textDecoration: "none", marginRight: 10, fontWeight: 500 }}>Files</a>
          <a href="/sessions" style={{ color: "#ffbf36", textDecoration: "none", marginRight: 16, fontWeight: 500 }}>Sessions</a>
          <span
            aria-label={recording ? "Voice recording" : "Idle"}
            style={{
              display: "inline-flex",
              alignItems: "center",
              fontSize: 18,
              color: recording ? "#2ecc40" : "#888",
              marginRight: 6,
              transition: "color 0.2s"
            }}
            title={recording ? "Recording (Ctrl+Shift+G held)" : "Push-to-talk: Ctrl+Shift+G"}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" style={{ marginRight: 3 }}>
              <ellipse cx="12" cy="12" rx="6" ry="9" fill={recording ? "#2ecc40" : "#333"} stroke="#777" strokeWidth="1.5"/>
              <rect x="8" y="18" width="8" height="2.5" rx="1.2" fill={recording ? "#2ecc40" : "#333"} stroke="#777" strokeWidth="1"/>
            </svg>
            <span style={{ fontSize: 13, color: "#aaa" }}>
              {recording ? "Listening..." : "Push-to-talk"}
            </span>
          </span>
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
          <Route path="/terminal" element={<TerminalPage />} />
          <Route path="/explorer" element={<FileExplorer />} />
          <Route path="/sessions" element={<SessionManager />} />
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