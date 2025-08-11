import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Chat from './pages/Chat';
import Scratchpad from './pages/Scratchpad';
import VoiceSettings from './pages/VoiceSettings';
import AutoTestReport from './pages/AutoTestReport';

import './styles/dark-hacker.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/scratchpad" element={<Scratchpad />} />
        <Route path="/voice-settings" element={<VoiceSettings />} />
        <Route path="/auto-test-report" element={<AutoTestReport />} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);