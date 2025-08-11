import React, { useState } from "react";
import { startAutoTest } from "../service/api";

export default function AutoTestReport() {
  const [target, setTarget] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleStart = async (e) => {
    e.preventDefault();
    if (!target.trim()) return;
    setLoading(true);
    setStatus("");
    try {
      await startAutoTest(target);
      setStatus("Auto test has been queued successfully!");
    } catch (err) {
      setStatus("Failed to queue auto test: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="grid-container">
      <div className="callout alert">
        <h2>🚀 Auto Test Reporting</h2>
        <form onSubmit={handleStart} className="grid-x grid-padding-x align-middle">
          <div className="cell auto">
            <input
              className="dark-theme"
              type="text"
              placeholder="Enter target (IP, URL, or domain)"
              value={target}
              onChange={e => setTarget(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="cell shrink">
            <button
              type="submit"
              className="button success"
              disabled={loading || !target.trim()}
              style={{ minWidth: 140 }}
            >
              {loading ? "Starting..." : "Start Auto Test"}
            </button>
          </div>
        </form>
        {status && (
          <div className="callout" style={{ marginTop: 16, background: "#23272c", color: "#e0e0e0" }}>
            {status}
          </div>
        )}
      </div>
    </div>
  );
}