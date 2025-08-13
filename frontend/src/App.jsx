import { useEffect, useRef, useState } from "react";
import Editor from "./components/Editor.jsx";
import TestRunner from "./components/TestRunner.jsx";
import "./styles/global.css";

const SAMPLE = `
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
    }).then((r) => r.json());
    setCpp(res.cpp || "");
  };

  useEffect(() => {
    const onKey = (e) => {
      const active = document.activeElement;
      const inEditor =
        active && active.classList && (active.classList.contains("code-input") || active.classList.contains("editor"));

      // Cmd+Enter → run
      if (e.metaKey && e.key === "Enter") {
        e.preventDefault();
        runnerRef.current?.runBoth?.();
        return;
      }
      // Cmd+' or Cmd+" → transpile (only when NOT typing inside the editor)
      if (!inEditor && e.metaKey && (e.key === "'" || e.key === '"')) {
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
          <button onClick={transpile} title={`Cmd+' or Cmd+" (when focus not in editor)`}>
            Transpile → C++ (AI)
          </button>
          <span className="status" style={{ marginLeft: 8 }}>
            Shortcuts: Cmd+' / Cmd+" (global), Cmd+Enter (run), Cmd+/ (toggle comments)
          </span>
        </div>
      </div>

      <div className="pane">
        <h3>Generated C++ (editable)</h3>
        <Editor value={cpp} onChange={setCpp} lang="cpp" />
      </div>

      <TestRunner ref={runnerRef} python={py} cpp={cpp} />
    </div>
  );
}
