import React, { useEffect, useState, useRef } from "react";
import { getVoices, textToSpeech } from "../service/api";

const PROVIDERS = [
  { value: "elevenlabs", label: "ElevenLabs (cloud)" },
  { value: "piper", label: "Piper (local/free)" }
];

export default function VoiceSettings() {
  const [voices, setVoices] = useState({});
  const [voiceId, setVoiceId] = useState("");
  const [provider, setProvider] = useState("elevenlabs");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");
  const audioRef = useRef();

  useEffect(() => {
    async function fetchVoices() {
      setError("");
      try {
        const res = await getVoices();
        setVoices(res.voices || {});
        const ids = Object.keys(res.voices || {});
        if (ids.length > 0) setVoiceId(ids[0]);
      } catch (err) {
        setError("Failed to load voices: " + err.message);
      }
    }
    fetchVoices();
  }, []);

  const handleSpeak = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setAudioUrl("");
    try {
      const blob = await textToSpeech(text, voiceId, provider);
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      setTimeout(() => {
        if (audioRef.current) audioRef.current.play();
      }, 50);
    } catch (err) {
      setError("TTS Error: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="grid-container">
      <div className="callout warning">
        <h2>🎤 Voice Settings</h2>
        <form className="grid-y" style={{ gap: 16 }} onSubmit={handleSpeak}>
          <label>
            Provider
            <select
              value={provider}
              onChange={e => setProvider(e.target.value)}
              disabled={loading}
              className="dark-theme"
              style={{ marginBottom: 8 }}
            >
              {PROVIDERS.map(p => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </label>
          <label>
            Voice
            <select
              value={voiceId}
              onChange={e => setVoiceId(e.target.value)}
              disabled={loading || Object.keys(voices).length === 0}
              className="dark-theme"
            >
              {Object.entries(voices).map(([id, name]) => (
                <option key={id} value={id}>{name || id}</option>
              ))}
            </select>
          </label>
          <label>
            Text
            <textarea
              className="dark-theme"
              rows={3}
              placeholder="Enter text to synthesize"
              value={text}
              onChange={e => setText(e.target.value)}
              disabled={loading}
              style={{ resize: "vertical" }}
            />
          </label>
          <button
            className="button success"
            type="submit"
            disabled={loading || !text.trim()}
            style={{ minWidth: 120 }}
          >
            {loading ? (
              <>
                <i className="fi-loop fi-spin" style={{ color: "#fff" }}></i> Speaking...
              </>
            ) : "Speak"}
          </button>
        </form>
        {audioUrl && (
          <div className="callout primary" style={{ marginTop: 16 }}>
            <audio ref={audioRef} src={audioUrl} controls />
          </div>
        )}
        {error && (
          <div className="callout alert" style={{ marginTop: 16 }}>
            {error}
          </div>
        )}
        <div className="subheader" style={{ marginTop: 12, color: "#aaa" }}>
          <strong>Note:</strong> Piper runs 100% locally (no cloud) and is free/open-source, but voices may be less natural than ElevenLabs.
        </div>
      </div>
    </div>
  );
}