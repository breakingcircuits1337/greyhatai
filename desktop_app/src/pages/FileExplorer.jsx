import React, { useState, useEffect } from "react";

function join(a, b) {
  if (a.endsWith("/")) return a + b;
  return a + "/" + b;
}

export default function FileExplorer() {
  const [path, setPath] = useState(window.process?.cwd?.() || "/");
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);

  function list(dir) {
    setLoading(true);
    window.api.list(dir).then(res => {
      setEntries(res);
      setLoading(false);
    });
  }

  useEffect(() => {
    const cwd = window.process?.cwd?.() || "/";
    setPath(cwd);
    setHistory([cwd]);
    list(cwd);
    // eslint-disable-next-line
  }, []);

  function handleDirClick(name) {
    const newPath = join(path, name);
    setPath(newPath);
    setHistory(h => [...h, newPath]);
    list(newPath);
  }

  function goUp() {
    const up = path.replace(/\/[^/]+\/?$/, "") || "/";
    setPath(up);
    setHistory(h => [...h, up]);
    list(up);
  }

  return (
    <div className="grid-container">
      <div className="callout" style={{ minHeight: 460, background: "#222" }}>
        <h4 style={{ marginBottom: 12 }}>File Explorer</h4>
        <div style={{ display: "flex", alignItems: "center", marginBottom: 12 }}>
          <input
            type="text"
            className="dark-theme"
            value={path}
            onChange={e => setPath(e.target.value)}
            style={{ flex: 1, marginRight: 8, minWidth: 120 }}
          />
          <button className="button" style={{ marginLeft: 8 }} onClick={() => list(path)}>
            Go
          </button>
          <button className="button secondary" onClick={goUp} style={{ marginLeft: 8 }}>
            Up
          </button>
        </div>
        {loading ? (
          <div className="subheader" style={{ color: "#aaa" }}>Loading...</div>
        ) : (
          <ul style={{
            listStyle: "none", padding: 0, margin: 0, background: "#181818",
            borderRadius: 4, border: "1px solid #333", minHeight: 250
          }}>
            {entries.map((entry, idx) => (
              <li
                key={idx}
                style={{
                  padding: "7px 14px",
                  cursor: entry.isDir ? "pointer" : "default",
                  color: entry.isDir ? "#49e" : "#e0e0e0",
                  fontWeight: entry.isDir ? "bold" : "normal"
                }}
                onClick={() => entry.isDir && handleDirClick(entry.name)}
              >
                {entry.isDir ? "📁 " : "📄 "}
                {entry.name}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}