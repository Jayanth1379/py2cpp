import { useEffect, useRef, useState } from "react";
import Editor from "./components/Editor.jsx";
import OutputPane from "./components/OutputPane.jsx";
import TestRunner from "./components/TestRunner.jsx";
import "./styles/global.css";

const SAMPLE = `# Example
n = int(input())
curr = 0
ans = 0
for _ in range(n):
    a, b = map(int, input().split())
    curr -= a
    curr += b
    ans = max(ans, curr)
print(ans)
`;

export default function App() {
  const [py, setPy] = useState(SAMPLE);
  const [cpp, setCpp] = useState("");
  const runnerRef = useRef(null);

  const transpile = async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/ai/convert`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ py })
    }).then(r => r.json());
    setCpp(res.cpp || "");
  };

  useEffect(() => {
    const onKey = (e) => {
      if (e.metaKey && e.key === "Enter") {
        e.preventDefault();
        runnerRef.current?.runBoth?.();
        return;
      }
      if (e.metaKey && (e.key === "'" || e.key === '"')) {
        e.preventDefault();
        transpile();
        return;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [py]);

  return (
    <div className="app">
      <div className="pane">
        <h3>Python</h3>
        <Editor value={py} onChange={setPy} lang="py" />
        <div className="controls">
          <button onClick={transpile} title={`Cmd+' or Cmd+"`}>Transpile → C++ (AI)</button>
          <span className="status" style={{ marginLeft: 8 }}>Shortcut: Cmd+' / Cmd+" • Cmd+Enter</span>
        </div>
      </div>
      <OutputPane title="Generated C++" text={cpp} />
      <TestRunner ref={runnerRef} python={py} cpp={cpp} />
    </div>
  );
}
