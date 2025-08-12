import subprocess, tempfile, os, textwrap, sys, shutil, glob

LIMIT_TIME = 2

FALLBACK_HEADERS = """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <queue>
#include <stack>
#include <deque>
#include <tuple>
#include <utility>
#include <sstream>
#include <iomanip>
#include <limits>
#include <array>
#include <bitset>
#include <functional>
#include <cstring>
#include <chrono>
using namespace std;
"""

def _run(cmd, stdin_str, cwd):
    try:
        p = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=cwd, text=True,
        )
        out, err = p.communicate(input=stdin_str, timeout=LIMIT_TIME + 1)
        return out, err, p.returncode, False
    except subprocess.TimeoutExpired:
        return "", "Time limit exceeded", -1, True

def run_python(code: str, stdin_str: str):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "main.py")
        with open(path, "w") as f: f.write(textwrap.dedent(code))
        return _run([sys.executable, path], stdin_str, d)

def _find_compiler():
    brew_gpp = sorted(
        glob.glob("/opt/homebrew/bin/g++-*") + glob.glob("/usr/local/bin/g++-*"),
        reverse=True
    )
    for c in brew_gpp:
        if shutil.which(c): return c, False  # not clang
    for c in ["g++", "clang++"]:
        if shutil.which(c): return c, (c == "clang++")
    return None, None

def _compile(cpp_code: str, d: str):
    cpp_path = os.path.join(d, "main.cpp")
    bin_path = os.path.join(d, "a.out")
    with open(cpp_path, "w") as f: f.write(cpp_code)

    compiler, is_clang = _find_compiler()
    if not compiler:
        return None, "No C++ compiler found. Install Xcode CLT or Homebrew GCC.", 127

    args = [compiler, "-std=gnu++17", "-O2", "-pipe", cpp_path, "-o", bin_path]
    if is_clang: args.insert(1, "-stdlib=libc++")

    comp = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=d)
    if comp.returncode != 0 and "bits/stdc++.h" in comp.stderr:
        fixed = cpp_code.replace("#include <bits/stdc++.h>", FALLBACK_HEADERS)
        with open(cpp_path, "w") as f: f.write(fixed)
        comp = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=d)

    return (bin_path if comp.returncode == 0 else None), comp.stderr, comp.returncode

def compile_cpp_only(cpp_code: str):
    with tempfile.TemporaryDirectory() as d:
        _, err, rc = _compile(cpp_code, d)
        return rc, err

def run_cpp(cpp_code: str, stdin_str: str):
    with tempfile.TemporaryDirectory() as d:
        bin_path, err, rc = _compile(cpp_code, d)
        if rc != 0:
            return "", err, rc, False
        return _run([bin_path], stdin_str, d)
