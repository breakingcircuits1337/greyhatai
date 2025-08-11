import React, { useState, useEffect } from "react";
import { chat as chatAPI, getModels } from "../service/api";

const PROVIDERS = [
  { name: "Ollama", value: "ollama" },
  { name: "Gemini", value: "gemini" },
  { name: "Mistral", value: "mistral" },
  { name: "Groq", value: "groq" },
];

export default function Chat() {
  const [provider, setProvider] = useState(PROVIDERS[0].value);
  const [models, setModels] = useState([]);
  const [model, setModel] = useState("");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="grid-container">
      <div className="callout primary">
        <h2>💬 Chat</h2>
        <div className="grid-x grid-margin-x align-middle">
          <div className="cell small-4">
            <label>
              Provider
              <select
                className="dark-theme"
                value={provider}
                onChange={e => setProvider(e.target.value)}
                disabled={loading}
              >
                {PROVIDERS.map(p => (
                  <option value={p.value} key={p.value}>{p.name}</option>
                ))}
              </select>
            </label>
          </div>
          <div className="cell small-4">
            <label>
              Model
              <select
                className="dark-theme"
                value={model}
                onChange={e => setModel(e.target.value)}
                disabled={loading || models.length === 0}
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
    </div>
  );
}