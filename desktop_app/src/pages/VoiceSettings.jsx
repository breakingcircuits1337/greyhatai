import React, { useEffect, useState, useRef } from "react";
import { getVoices, textToSpeech, startTraining, getTrainingStatus } from "../service/api";

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

  // Train New Voice states
  const [newVoiceId, setNewVoiceId] = useState("");
  const [transcript, setTranscript] = useState("");
  const [audioFile, setAudioFile] = useState(null);
  const [training, setTraining] = useState(false);
  const [jobId, setJobId] = useState("");
  const [progress, setProgress] = useState(0);
  const [trainStatus, setTrainStatus] = useState("");
  const [trainError, setTrainError] = useState("");

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

  // Train New Voice logic
  const handleTrain = async (e) => {
    e.preventDefault();
    setTrainError("");
    setTraining(true);
    setProgress(0);
    setTrainStatus("queued");
    try {
      const { job_id } = await startTraining(newVoiceId, transcript, audioFile);
      setJobId(job_id);
      pollStatus(job_id);
    } catch (err) {
      setTrainError("Training failed: " + err.message);
      setTraining(false);
    }
  };

  // Poll job status
  const pollStatus = (job_id) => {
    const poll = async () => {
      try {
        const res = await getTrainingStatus(job_id);
        setProgress(res.progress || 0);
        setTrainStatus(res.status || "");
        if (res.status === "completed" || res.status === "failed") {
          setTraining(false);
          if (res.status === "completed") {
            // Refresh voices on completion
            const v = await getVoices();
            setVoices(v.voices || {});
          }
        } else {
          setTimeout(() => pollStatus(job_id), 2000);
        }
      } catch (err) {
        setTrainError("Polling error: " + err.message);
        setTraining(false);
      }
    };
    poll();
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

        {/* Train New Voice Panel */}
        <div className="callout" style={{ marginTop: 30, background: "#181818", color: "#e0e0e0" }}>
          <h4>Train New Voice</h4>
          <form className="grid-y" style={{ gap: 12 }} onSubmit={handleTrain}>
            <label>
              New Voice ID
              <input
                type="text"
                value={newVoiceId}
                onChange={e => setNewVoiceId(e.target.value)}
                className="dark-theme"
                disabled={training}
              />
            </label>
            <label>
              Transcript (text matching audio content)
              <textarea
                rows={2}
                value={transcript}
                onChange={e => setTranscript(e.target.value)}
                className="dark-theme"
                disabled={training}
              />
            </label>
            <label>
              Audio File (.wav)
              <input
                type="file"
                accept=".wav,audio/wav"
                onChange={e => setAudioFile(e.target.files[0])}
                className="dark-theme"
                disabled={training}
              />
            </label>
            <button
              className="button success"
              type="submit"
              style={{ minWidth: 120 }}
              disabled={
                training ||
                !newVoiceId.trim() ||
                !transcript.trim() ||
                !audioFile
              }
            >
              {training ? "Training..." : "Start Training"}
            </button>
          </form>
          {training && (
            <div className="progress success" role="progressbar" tabIndex="0" aria-valuenow={progress} aria-valuemin="0" aria-valuemax="100" style={{ marginTop: 16 }}>
              <div className="progress-meter" style={{ width: `${progress}%` }}>
                {progress}%
              </div>
            </div>
          )}
          {trainStatus && !training && (
            <div className="callout" style={{ marginTop: 10, background: "#222", color: "#e0e0e0" }}>
              Training {trainStatus === "completed" ? "completed!" : trainStatus}
            </div>
          )}
          {trainError && (
            <div className="callout alert" style={{ marginTop: 10 }}>
              {trainError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}