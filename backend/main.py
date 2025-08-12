from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from transpiler.python_to_cpp import py_to_cpp
from runner.sandbox import run_python, run_cpp
from ai.llm import ai_convert_to_cpp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranspileReq(BaseModel):
    code: str

class ConvertReq(BaseModel):
    py: str

class RunReq(BaseModel):
    code: str
    stdin: str = ""

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/ai/convert")
def ai_convert(req: ConvertReq):
    cpp = ai_convert_to_cpp(req.py)
    return {"cpp": cpp}

@app.post("/transpile")
def transpile(req: TranspileReq):
    cpp = py_to_cpp(req.code)
    return {"cpp": cpp}

@app.post("/run/python")
def run_py(req: RunReq):
    out, err, rc, timed_out = run_python(req.code, req.stdin)
    return {"stdout": out, "stderr": err, "rc": rc, "timedOut": timed_out}

@app.post("/run/cpp")
def run_cpp_route(req: RunReq):
    out, err, rc, timed_out = run_cpp(req.code, req.stdin)
    return {"stdout": out, "stderr": err, "rc": rc, "timedOut": timed_out}
