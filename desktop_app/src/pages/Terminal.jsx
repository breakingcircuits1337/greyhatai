import React, { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";

export default function TerminalPage() {
  const xtermRef = useRef();
  const fitAddon = useRef(new FitAddon());
  const terminal = useRef(null);

  useEffect(() => {
    const term = new Terminal({
      fontFamily: "Fira Mono, monospace",
      fontSize: 16,
      theme: { background: "#1d1d1d", foreground: "#e0e0e0" }
    });
    terminal.current = term;
    term.loadAddon(fitAddon.current);
    term.open(xtermRef.current);
    fitAddon.current.fit();

    // Listen for data from backend
    window.api.onData(data => term.write(data));

    // Handle user input
    term.onData(data => window.api.send(data));

    // Start an initial shell
    window.api.exec(""); // Spawn shell

    // Fit on resize
    const handleResize = () => fitAddon.current.fit();
    window.addEventListener("resize", handleResize);
    fitAddon.current.fit();

    return () => {
      term.dispose();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <div className="grid-container">
      <div className="callout" style={{ minHeight: 500, background: "#222", padding: 0 }}>
        <h4 style={{ padding: "0.8rem 1.5rem", margin: 0, borderBottom: "1px solid #333" }}>
          Embedded Terminal
        </h4>
        <div ref={xtermRef} style={{ width: "100%", height: "430px" }} />
      </div>
    </div>
  );
}