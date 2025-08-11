import React, { useState, useEffect, useRef } from "react";

// Helper to join paths
function join(a, b) {
  if (a.endsWith("/")) return a + b;
  return a + "/" + b;
}

// Tree node: { name, path, isDir, children, expanded }
function toNode(entry, parentPath) {
  return {
    name: entry.name,
    path: entry.path || join(parentPath, entry.name),
    isDir: entry.isDir,
    children: entry.isDir ? [] : null,
    expanded: false,
    isFile: entry.isFile
  };
}

export default function FileExplorer() {
  const [root, setRoot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPath, setCurrentPath] = useState("/");
  const [preview, setPreview] = useState(null);
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, node: null });
  const explorerRef = useRef();

  // Initial load
  useEffect(() => {
    let cwd = "/";
    try {
      cwd = window.process?.cwd?.() || "/";
    } catch {}
    setCurrentPath(cwd);
    window.api.list(cwd).then(entries => {
      setRoot({
        name: cwd,
        path: cwd,
        isDir: true,
        expanded: true,
        children: entries.map(e => toNode(e, cwd))
      });
      setLoading(false);
    });
    // eslint-disable-next-line
  }, []);

  // Context menu close on click outside
  useEffect(() => {
    const handler = () => setContextMenu({ visible: false, x: 0, y: 0, node: null });
    window.addEventListener("click", handler);
    return () => window.removeEventListener("click", handler);
  }, []);

  // Tree expand/collapse and lazy loading
  function handleExpand(node) {
    if (!node.expanded) {
      // Lazy-load children
      window.api.list(node.path).then(entries => {
        node.children = entries.map(e => toNode(e, node.path));
        node.expanded = true;
        setRoot({ ...root });
      });
    } else {
      node.expanded = false;
      setRoot({ ...root });
    }
  }

  // Context menu open
  function handleContextMenu(e, node) {
    e.preventDefault();
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      node
    });
  }

  // Preview file
  async function handlePreview(node) {
    setContextMenu({ visible: false, x: 0, y: 0, node: null });
    const res = await window.api.readFile(node.path);
    setPreview({ ...res, name: node.name, path: node.path });
  }

  // Open in system
  function handleOpen(node) {
    setContextMenu({ visible: false, x: 0, y: 0, node: null });
    window.api.openPath(node.path);
  }

  // Tree rendering
  function renderNode(node, level = 0) {
    return (
      <div key={node.path} style={{ marginLeft: 12 * level, userSelect: "none", position: "relative" }}>
        <span
          style={{
            cursor: node.isDir ? "pointer" : "default",
            color: node.isDir ? "#49e" : "#e0e0e0",
            fontWeight: node.isDir ? "bold" : "normal"
          }}
          onClick={() => node.isDir && handleExpand(node)}
          onContextMenu={e => handleContextMenu(e, node)}
        >
          {node.isDir ? (node.expanded ? "📂" : "📁") : "📄"} {node.name}
        </span>
        {node.expanded && node.children && node.children.length > 0 && (
          <div>
            {node.children.map(child => renderNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  }

  // File preview rendering
  function renderPreview() {
    if (!preview) return <div className="subheader" style={{ color: "#888" }}>No file selected.</div>;
    if (preview.text) {
      return (
        <div>
          <div style={{ fontWeight: "bold", marginBottom: 6 }}>{preview.name}</div>
          <pre style={{
            background: "#111", padding: 12, color: "#e0e0e0",
            maxHeight: 400, overflow: "auto"
          }}>{preview.text}</pre>
        </div>
      );
    }
    if (preview.dataUrl) {
      return (
        <div>
          <div style={{ fontWeight: "bold", marginBottom: 6 }}>{preview.name}</div>
          <img src={preview.dataUrl} alt={preview.name} style={{ maxWidth: "100%", maxHeight: 380, borderRadius: 4 }} />
        </div>
      );
    }
    if (preview.error) {
      return <div style={{ color: "red" }}>Error: {preview.error}</div>;
    }
    return <div>Cannot preview this file.</div>;
  }

  // Context menu rendering
  function renderContextMenu() {
    if (!contextMenu.visible || !contextMenu.node) return null;
    const style = {
      position: "fixed",
      zIndex: 1000,
      top: contextMenu.y + 2,
      left: contextMenu.x + 2,
      background: "#23272c",
      color: "#fff",
      boxShadow: "0 1px 8px rgba(0,0,0,0.23)",
      padding: "4px 0",
      borderRadius: 5,
      minWidth: 120
    };
    return (
      <div style={style}>
        {contextMenu.node.isFile && (
          <div
            onClick={() => handlePreview(contextMenu.node)}
            style={{ padding: "7px 18px", cursor: "pointer", borderBottom: "1px solid #333" }}
          >Preview</div>
        )}
        <div
          onClick={() => handleOpen(contextMenu.node)}
          style={{ padding: "7px 18px", cursor: "pointer" }}
        >Open</div>
      </div>
    );
  }

  return (
    <div className="grid-container" ref={explorerRef}>
      <div className="callout" style={{ minHeight: 460, background: "#222", display: "flex", flexDirection: "row", gap: 0 }}>
        <div style={{
          width: 320, minWidth: 180, padding: 8, borderRight: "1.5px solid #333",
          background: "#20282a", maxHeight: 480, overflow: "auto"
        }}>
          <div style={{ fontWeight: "bold", marginBottom: 10, color: "#7fd" }}>File System</div>
          {loading || !root ? (
            <div className="subheader" style={{ color: "#aaa" }}>Loading...</div>
          ) : (
            <div>{renderNode(root)}</div>
          )}
        </div>
        <div style={{ flex: 1, minWidth: 0, padding: 16 }}>
          <div style={{ fontWeight: "bold", marginBottom: 10, color: "#39f369" }}>Preview</div>
          <div>{renderPreview()}</div>
        </div>
        {renderContextMenu()}
      </div>
    </div>
  );
}