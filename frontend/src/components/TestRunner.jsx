import React, { forwardRef, useImperativeHandle, useState } from "react";

function TestRunnerImpl({ python, cpp }) {
  const [stdin, setStdin] = useState("");
  const [pyOut, setPyOut] = useState("");
  const [cppOut, setCppOut] = useState("");
  const [status, setStatus] = useState("");

  const API = import.meta.env.VITE_API_URL;

  const runBoth = async () => {
    setStatus("Running…");
    try {
      const py = await fetch(`${API}/run/python`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: python, stdin })
      }).then(r => r.json());

      const cc = await fetch(`${API}/run/cpp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: cpp, stdin })
      }).then(r => r.json());

      setPyOut((py.stdout || "") + (py.stderr ? ("\n[stderr]\n" + py.stderr) : ""));
      setCppOut((cc.stdout || "") + (cc.stderr ? ("\n[stderr]\n" + cc.stderr) : ""));
    } finally {
      setStatus("");
    }
  };

  useImperativeHandle(
    arguments[1],
    () => ({ runBoth })
  );

  return (
    <div className="pane">
      <h3>Test runner</h3>
      <div className="io">
        <textarea
          className="editor"
          placeholder="stdin…"
          value={stdin}
          onChange={(e) => setStdin(e.target.value)}
        />
      </div>
      <div className="controls">
        <button onClick={runBoth}>Run Python & C++</button>
        {status && <div className="status">{status}</div>}
      </div>
      <div style={{ display: "flex", gap: 8, padding: 8, height: "100%" }}>
        <div className="pane" style={{ flex: 1 }}>
          <h3>Python output</h3>
          <pre className="output">{pyOut}</pre>
        </div>
        <div className="pane" style={{ flex: 1 }}>
          <h3>C++ output</h3>
          <pre className="output">{cppOut}</pre>
        </div>
      </div>
    </div>
  );
}

const TestRunner = forwardRef(TestRunnerImpl);
export default TestRunner;
