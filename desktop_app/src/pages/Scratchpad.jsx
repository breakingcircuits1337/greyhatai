import React, { useEffect, useState } from "react";
import { getScratchpad, clearScratchpad } from "../service/api";

export default function Scratchpad() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  async function fetchScratchpad() {
    setLoading(true);
    try {
      const data = await getScratchpad();
      setEntries(data.scratchpad || []);
    } catch (err) {
      setEntries([{ role: "error", content: err.message }]);
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchScratchpad();
    // eslint-disable-next-line
  }, []);

  const handleClear = async () => {
    setClearing(true);
    try {
      await clearScratchpad();
      setEntries([]);
    } catch (err) {
      setEntries([{ role: "error", content: err.message }]);
    }
    setClearing(false);
  };

  return (
    <div className="grid-container">
      <div className="callout secondary">
        <h2>📝 Agent Scratchpad</h2>
        <div style={{ minHeight: 200, background: "#23272c", borderRadius: 8, padding: 16, margin: "1rem 0" }}>
          {loading ? (
            <div className="text-center">
              <i className="fi-loop fi-spin" style={{ fontSize: 24, color: "#2ecc40" }}></i>
              <span> Loading scratchpad...</span>
            </div>
          ) : entries.length === 0 ? (
            <div className="subheader" style={{ color: "#888" }}>Scratchpad is empty.</div>
          ) : (
            entries.map((entry, idx) => (
              <div key={idx} className={entry.role === "user" ? "callout success" :
                                        entry.role === "assistant" ? "callout primary" :
                                        "callout alert"} style={{ marginBottom: 8 }}>
                <strong>{entry.role.charAt(0).toUpperCase() + entry.role.slice(1)}</strong>
                <div style={{ marginTop: 2, whiteSpace: "pre-wrap" }}>{entry.content}</div>
              </div>
            ))
          )}
        </div>
        <button className="button alert" onClick={handleClear} disabled={clearing || loading}>
          {clearing ? "Clearing..." : "Clear Scratchpad"}
        </button>
      </div>
    </div>
  );
}