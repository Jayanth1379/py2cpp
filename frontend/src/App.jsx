import { useState } from "react";
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

  const API = import.meta.env.VITE_API_URL;

  const transpile = async () => {
    const res = await fetch(`${API}/ai/convert`, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ py })
    }).then(r=>r.json());
    setCpp(res.cpp || "");
  };

  return (
    <div className="app">
      <div className="pane">
        <h3>Python</h3>
        <Editor value={py} onChange={setPy}/>
        <div className="controls">
          <button onClick={transpile}>Transpile → C++ (AI)</button>
        </div>
      </div>
      <OutputPane title="Generated C++" text={cpp}/>
      <TestRunner python={py} cpp={cpp}/>
    </div>
  );
}
