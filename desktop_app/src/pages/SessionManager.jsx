import React, { useEffect, useState } from "react";
import { listSessions, saveSession, loadSession, deleteSession } from "../service/api";

export default function SessionManager() {
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState("");
  const [saveName, setSaveName] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [loaded, setLoaded] = useState(null);

  const refresh = async () => {
    const res = await listSessions();
    setSessions(res.sessions || []);
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleSave = async () => {
    if (!saveName.trim()) return;
    setLoading(true);
    try {
      await saveSession(saveName);
      setMessage("Session saved.");
      setSaveName("");
      refresh();
    } catch (err) {
      setMessage("Save failed: " + err.message);
    }
    setLoading(false);
  };

  const handleLoad = async (name) => {
    setLoading(true);
    setLoaded(null);
    try {
      const data = await loadSession(name);
      setLoaded(data);
      setMessage("Session loaded.");
    } catch (err) {
      setMessage("Load failed: " + err.message);
    }
    setLoading(false);
  };

  const handleDelete = async (name) => {
    setLoading(true);
    try {
      await deleteSession(name);
      setMessage("Session deleted.");
      refresh();
    } catch (err) {
      setMessage("Delete failed: " + err.message);
    }
    setLoading(false);
  };

  const handleExport = () => {
    if (!loaded) return;
    const data = JSON.stringify(loaded, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "greyhatai_session.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="grid-container">
      <div className="callout" style={{ maxWidth: 700, margin: "0 auto" }}>
        <h3>Session Manager</h3>
        <div style={{ marginBottom: 16 }}>
          <input
            type="text"
            className="dark-theme"
            style={{ marginRight: 8 }}
            value={saveName}
            onChange={e => setSaveName(e.target.value)}
            placeholder="Session name"
            disabled={loading}
          />
          <button className="button success" style={{ minWidth: 110 }} onClick={handleSave} disabled={loading || !saveName.trim()}>
            Save Current Session
          </button>
        </div>
        <div>
          <strong>Saved Sessions:</strong>
          <ul style={{ margin: "10px 0 18px 0" }}>
            {sessions.map(name => (
              <li key={name} style={{ marginBottom: 6 }}>
                <span style={{ marginRight: 14 }}>{name}</span>
                <button className="button tiny" onClick={() => handleLoad(name)} disabled={loading}>Load</button>
                <button className="button alert tiny" style={{ marginLeft: 6 }} onClick={() => handleDelete(name)} disabled={loading}>Delete</button>
              </li>
            ))}
          </ul>
        </div>
        {message && <div className="callout" style={{ margin: "10px 0" }}>{message}</div>}
        {loaded && (
          <div className="callout primary" style={{ marginTop: 24, background: "#1c2327" }}>
            <h5>Loaded Session</h5>
            <button className="button secondary tiny" onClick={handleExport} style={{ float: "right", marginLeft: 8 }}>Export as JSON</button>
            <pre style={{ background: "#161b1f", color: "#e0e0e0", fontSize: 13, padding: 12, maxHeight: 240, overflow: "auto" }}>
              {JSON.stringify(loaded, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}