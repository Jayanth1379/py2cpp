# py2cpp — AI Python → C++ (CF-ready)

[![Vercel](https://img.shields.io/badge/Frontend-Vercel-black?logo=vercel)](https://py2cpp.vercel.app/)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009485?logo=fastapi)
![Ollama](https://img.shields.io/badge/LLM-Ollama-000?logo=ollama)
![Model](https://img.shields.io/badge/Qwen2.5--Coder-7B-blue)
![License](https://img.shields.io/badge/License-MIT-informational)

**py2cpp** converts Python to C++17 with a Codeforces-style boilerplate, then compiles and runs both versions side-by-side on the same input.  
AI-first: Qwen2.5-Coder (via Ollama) + a compile-and-repair loop.  
**Live UI:** https://py2cpp.vercel.app/

---

## Requirements
- macOS with Homebrew
- Python 3.10+, Node 18+
- Ollama installed

---

## Quick start

1) **Model server**
```bash
brew install ollama cloudflare/cloudflare/cloudflared
ollama serve
ollama pull qwen2.5-coder:7b
```

2) **Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OLLAMA_MODEL=qwen2.5-coder:7b
uvicorn main:app --host 0.0.0.0 --port 8000
```

3) **Frontend**
```bash
cd frontend
echo "VITE_API_URL=https://<your-tunnel>.trycloudflare.com" > .env
npm install && npm run dev
```
> The frontend is static. The backend (FastAPI + Ollama + g++) runs on your machine and must stay running.

4) **Public URL**
```bash
cloudflared tunnel --url http://localhost:8000
# copy the https://<random>.trycloudflare.com URL
```

### Notes:  Deployment can be only for frontend via netlify or vercel ; backend would be running locally constantly to work

## API

- POST /ai/convert → body { "py": "<python>" } → { "cpp": "<full c++ file>" }

- POST /run/python → { "code": "<python>", "stdin": "<input>" }

- POST /run/cpp → { "code": "<c++>", "stdin": "<input>" }

- GET /healthz → { "ok": true }


### Key points:

- macOS/Clang is handled by a fallback header set when <bits/stdc++.h> is unavailable.

- Targeted at contest-style Python; highly dynamic features may require manual edits.

### License
MIT © Birajit Saikia
