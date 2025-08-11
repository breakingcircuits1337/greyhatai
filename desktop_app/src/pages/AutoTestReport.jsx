import React, { useState, useRef, useEffect } from "react";
import { startAutoTest } from "../service/api";
// For Mermaid integration:
import mermaid from "mermaid";

export default function AutoTestReport() {
  const [target, setTarget] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState("");
  const mermaidRef = useRef();

  // Helper to fetch the report
  async function fetchReport(target) {
    try {
      const res = await fetch(`http://localhost:8000/auto-test/results?target=${encodeURIComponent(target)}`);
      if (!res.ok) throw new Error((await res.json()).detail || "Failed to fetch report");
      const data = await res.json();
      setReport(data.report);
      setStatus("Auto test complete!");
    } catch (err) {
      setError(err.message);
    }
  }

  // Poll for report completion after submitting auto-test
  useEffect(() => {
    if (!polling || !target) return;
    let timer;
    const poll = async () => {
      try {
        const res = await fetch(`http://localhost:8000/auto-test/results?target=${encodeURIComponent(target)}`);
        if (res.ok) {
          const data = await res.json();
          setReport(data.report);
          setStatus("Auto test complete!");
          setPolling(false);
          setLoading(false);
        } else {
          // Not ready, keep polling
          timer = setTimeout(poll, 1500);
        }
      } catch {
        timer = setTimeout(poll, 1500);
      }
    };
    poll();
    return () => clearTimeout(timer);
    // eslint-disable-next-line
  }, [polling, target]);

  // Render Mermaid after report loads
  useEffect(() => {
    if (report && report.reconnaissance && report.reconnaissance.diagram && mermaidRef.current) {
      mermaid.initialize({ startOnLoad: false, theme: "dark" });
      mermaid.render(
        "mermaid-diagram",
        report.reconnaissance.diagram,
        (svg) => {
          mermaidRef.current.innerHTML = svg;
        }
      );
    }
  }, [report]);

  const handleStart = async (e) => {
    e.preventDefault();
    setReport(null);
    setError("");
    setStatus("");
    if (!target.trim()) return;
    setLoading(true);
    try {
      await startAutoTest(target);
      setStatus("Auto test started. Please wait...");
      setPolling(true);
    } catch (err) {
      setError("Failed to queue auto test: " + err.message);
      setLoading(false);
    }
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
              disabled={loading || polling}
            />
          </div>
          <div className="cell shrink">
            <button
              type="submit"
              className="button success"
              disabled={loading || !target.trim() || polling}
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
        {error && (
          <div className="callout alert" style={{ marginTop: 16 }}>
            {error}
          </div>
        )}
        {report && (
          <div style={{ marginTop: 32 }}>
            <AccordionReport report={report} mermaidRef={mermaidRef} />
          </div>
        )}
      </div>
    </div>
  );
}

// Accordion using Foundation classes (or react-accordion if installed)
function AccordionReport({ report, mermaidRef }) {
  // Fallback to basic collapsible if Foundation's JS is not loaded
  return (
    <ul className="accordion" data-accordion data-allow-all-closed="true" style={{ background: "#222" }}>
      <li className="accordion-item is-active" data-accordion-item>
        <a href="#summary" className="accordion-title">Summary</a>
        <div className="accordion-content" data-tab-content>
          <strong>Target:</strong> {report.target}<br />
          {report.summary}
        </div>
      </li>
      <li className="accordion-item" data-accordion-item>
        <a href="#recon" className="accordion-title">Reconnaissance</a>
        <div className="accordion-content" data-tab-content>
          <div ref={mermaidRef} className="mermaid" style={{ background: "#181818", padding: 12, borderRadius: 8, marginBottom: 8 }}></div>
          <ul>
            {report.reconnaissance.findings.map((finding, idx) => (
              <li key={idx}>{finding}</li>
            ))}
          </ul>
        </div>
      </li>
      <li className="accordion-item" data-accordion-item>
        <a href="#vulns" className="accordion-title">Vulnerabilities</a>
        <div className="accordion-content" data-tab-content>
          <ul>
            {report.vulnerabilities.map((vuln, idx) => (
              <li key={idx}>
                <strong>{vuln.id}</strong>: {vuln.desc} (<span style={{ color: vuln.severity === "high" ? "red" : "#ffc107" }}>{vuln.severity}</span>)
              </li>
            ))}
          </ul>
        </div>
      </li>
      <li className="accordion-item" data-accordion-item>
        <a href="#exploit" className="accordion-title">Exploitation Plan</a>
        <div className="accordion-content" data-tab-content>
          <ol>
            {report.exploitation.plan.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      </li>
    </ul>
  );
}

/*
Instructions for integrating Mermaid:
1. Install Mermaid: 
   npm install mermaid

2. Import mermaid in this file:
   import mermaid from "mermaid";

3. Use mermaid.render() to render diagrams as shown above, after the report is loaded.

4. Ensure Foundation's accordion JS is loaded if you want full UI behavior, or use a React accordion lib.
*/