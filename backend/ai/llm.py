import json, os, re, requests

from runner.sandbox import compile_cpp_only

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

CF_BOILERPLATE = r"""
#include <bits/stdc++.h>
using namespace std;

// fast io
#define fastio ios::sync_with_stdio(false); cin.tie(nullptr)
#define endl '\n'

// shorthands
#define all(x) begin(x), end(x)
#define rall(x) rbegin(x), rend(x)
#define pb push_back
#define ff first
#define ss second
#define sz(x) (int((x).size()))

using ll  = long long;
using ld  = long double;
using pii = pair<int,int>;
using pll = pair<ll,ll>;
using vi  = vector<int>;
using vll = vector<ll>;

// constants
const ll INF = (ll)1e18;
const int MOD = 1e9 + 7;
const ld EPS = 1e-9;
const int dx[4] = {1, 0, -1, 0};
const int dy[4] = {0, 1, 0, -1};

// debug (enable with -DLOCAL)
#ifdef LOCAL
  #define debug(x) cerr << #x << " = " << (x) << endl
#else
  #define debug(x) ((void)0)
#endif

void solve() {
    // write solution here
}

int main() {
    fastio;
    int t = 1;
    // cin >> t; // multiple tests
    while (t--) solve();
    return 0;
}
"""

SYSTEM = f"""You are an elite competitive programmer and C++ translator.
Convert the user's Python into ONE self-contained C++17 program that compiles with GNU g++.
HARD RULES:
- Copy the boilerplate exactly as given and write ALL logic inside solve().
- Preserve input/output behavior. Read from stdin, write to stdout. No prompts.
- Prefer long long for integers and vector<long long> for int lists where applicable.
- No extra libraries beyond <bits/stdc++.h>. No extra commentary.
Return ONLY the full C++ file in a single fenced code block.
Boilerplate:
{CF_BOILERPLATE}
"""

USER_TEMPLATE = """Convert this Python to C++ (write logic inside solve()). Keep the same I/O:

```python
{py}
```"""

def _ollama_generate(model: str, prompt: str, system: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": True,
        "options": {"temperature": 0.15, "top_p": 0.9}
    }
    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=600)
    r.raise_for_status()
    text = ""
    for line in r.iter_lines(decode_unicode=True):
        if not line: continue
        obj = json.loads(line)
        text += obj.get("response", "")
        if obj.get("done"): break
    return text

def _extract_code(text: str) -> str:
    m = re.search(r"```(?:cpp|c\+\+|cc|cxx)?\s*(.*?)```", text, flags=re.S|re.I)
    return (m.group(1) if m else text).strip()

def ai_convert_to_cpp(py_src: str, max_repairs: int = 2) -> str:
    out = _ollama_generate(MODEL, USER_TEMPLATE.format(py=py_src), SYSTEM)
    cpp = _extract_code(out)

    for _ in range(max_repairs + 1):
        rc, err = compile_cpp_only(cpp)
        if rc == 0:
            return cpp
        repair_prompt = (
            "The C++ failed to compile with these errors:\n\n"
            f"{err}\n\n"
            "Fix and reprint the FULL corrected C++ file. Keep the SAME boilerplate and constraints. "
            "Return ONLY the code in one fenced code block."
        )
        out = _ollama_generate(MODEL, repair_prompt, SYSTEM)
        cpp = _extract_code(out)

    return cpp
