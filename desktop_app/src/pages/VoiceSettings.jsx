import React, { useEffect, useState, useRef } from "react";
import { getVoices, textToSpeech } from "../service/api";

export default function VoiceSettings() {
  const [voices, setVoices] = useState({});
  const [voiceId, setVoiceId] = useState("");
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
        // Set default voice
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
      const blob = await textToSpeech(text, voiceId);
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      // Play automatically
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
      </div>
    </div>
  );
}