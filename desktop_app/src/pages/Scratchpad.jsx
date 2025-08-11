import React, { useEffect, useState } from "react";
import { getScratchpad, clearScratchpad } from "../service/api";
import { Responsive, WidthProvider } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = WidthProvider(Responsive);

function getSavedLayout(key, fallback) {
  try {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : fallback;
  } catch {
    return fallback;
  }
}
function saveLayout(key, layout) {
  localStorage.setItem(key, JSON.stringify(layout));
}

export default function Scratchpad() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  // Layout state
  const defaultLayouts = {
    lg: [
      { i: "scratchpad-panel", x: 0, y: 0, w: 12, h: 8, minW: 5, minH: 6 }
    ]
  };
  const [layouts, setLayouts] = useState(() => getSavedLayout("scratchpadGridLayout", defaultLayouts));

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

  function handleLayoutChange(newLayout, allLayouts) {
    setLayouts(allLayouts);
    saveLayout("scratchpadGridLayout", allLayouts);
  }

  return (
    <div className="grid-container">
      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 2 }}
        rowHeight={50}
        onLayoutChange={handleLayoutChange}
        draggableHandle=".panel-header"
      >
        <div key="scratchpad-panel" className="callout secondary" style={{ overflow: "auto" }}>
          <div className="panel-header" style={{ cursor: "move", marginBottom: 10 }}>
            <h2 style={{ margin: 0 }}>📝 Agent Scratchpad</h2>
          </div>
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
      </ResponsiveGridLayout>
    </div>
  );
}