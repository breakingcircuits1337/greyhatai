import React, { useState, useEffect } from "react";
import { chat as chatAPI, getModels } from "../service/api";
import { Responsive, WidthProvider } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = WidthProvider(Responsive);

const PROVIDERS = [
  { name: "Ollama", value: "ollama" },
  { name: "Gemini", value: "gemini" },
  { name: "Mistral", value: "mistral" },
  { name: "Groq", value: "groq" },
];

// Persist layout in localStorage
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

export default function Chat() {
  const [provider, setProvider] = useState(PROVIDERS[0].value);
  const [models, setModels] = useState([]);
  const [model, setModel] = useState("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Layout state
  const defaultLayouts = {
    lg: [
      { i: "chat-panel", x: 0, y: 0, w: 12, h: 8, minW: 5, minH: 6 }
    ]
  };
  const [layouts, setLayouts] = useState(() => getSavedLayout("chatGridLayout", defaultLayouts));

  useEffect(() => {
    async function fetchModels() {
      const result = await getModels(provider);
      setModels(result.models || []);
      setModel(result.models?.[0] || "");
    }
    fetchModels();
  }, [provider]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    setMessages((msgs) => [
      ...msgs,
      { role: "user", content: message },
    ]);
    try {
      const res = await chatAPI({ message, provider, model });
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: res.content, provider: res.provider, model: res.model },
      ]);
      setMessage("");
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { role: "assistant", content: "Error: " + err.message },
      ]);
    }
    setLoading(false);
  };

  function handleLayoutChange(newLayout, allLayouts) {
    setLayouts(allLayouts);
    saveLayout("chatGridLayout", allLayouts);
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
        <div key="chat-panel" className="callout primary" style={{ overflow: "auto" }}>
          <div className="panel-header" style={{ cursor: "move", marginBottom: 10, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <h2 style={{ margin: 0 }}>💬 Chat</h2>
            <div className="grid-x grid-margin-x align-middle" style={{ marginRight: 0 }}>
              <div className="cell auto">
                <label style={{ fontSize: 13 }}>
                  Provider
                  <select
                    className="dark-theme"
                    value={provider}
                    onChange={e => setProvider(e.target.value)}
                    disabled={loading}
                    style={{ marginLeft: 6 }}
                  >
                    {PROVIDERS.map(p => (
                      <option value={p.value} key={p.value}>{p.name}</option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="cell auto">
                <label style={{ fontSize: 13, marginLeft: 10 }}>
                  Model
                  <select
                    className="dark-theme"
                    value={model}
                    onChange={e => setModel(e.target.value)}
                    disabled={loading || models.length === 0}
                    style={{ marginLeft: 6 }}
                  >
                    {models.length === 0
                      ? <option value="">Default</option>
                      : models.map(m => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                  </select>
                </label>
              </div>
            </div>
          </div>
          <div className="chat-window" style={{ minHeight: 250, maxHeight: 350, overflowY: "auto", background: "#23272c", borderRadius: 8, padding: 16, margin: "1rem 0" }}>
            {messages.length === 0 && <div className="text-center subheader" style={{ color: "#888" }}>No messages yet.</div>}
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === "user" ? "callout success" : "callout secondary"} style={{ marginBottom: 8 }}>
                <strong>{msg.role === "user" ? "You" : "AI"}</strong>
                <span style={{ float: "right", fontSize: 12, color: "#aaa" }}>
                  {msg.provider && msg.model && msg.role === "assistant" ? `[${msg.provider} – ${msg.model}]` : ""}
                </span>
                <div style={{ marginTop: 2, whiteSpace: "pre-wrap" }}>{msg.content}</div>
              </div>
            ))}
            {loading && (
              <div className="text-center">
                <i className="fi-loop fi-spin" style={{ fontSize: 24, color: "#2ecc40" }}></i> <span>Waiting for AI...</span>
              </div>
            )}
          </div>
          <form onSubmit={handleSubmit} className="grid-x grid-padding-x align-middle">
            <div className="cell auto">
              <input
                className="dark-theme"
                type="text"
                placeholder="Type your message..."
                value={message}
                disabled={loading}
                onChange={e => setMessage(e.target.value)}
                autoFocus
              />
            </div>
            <div className="cell shrink">
              <button type="submit" className="button success" disabled={loading || !message.trim()} style={{ minWidth: 120 }}>
                {loading ? "Sending..." : "Send"}
              </button>
            </div>
          </form>
        </div>
      </ResponsiveGridLayout>
    </div>
  );
}