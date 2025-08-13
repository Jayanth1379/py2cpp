import { useEffect, useRef, useState } from "react";

const INDENT = "    ";
const INDENT_LEN = INDENT.length;
const OPENERS = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'" };
const CLOSERS = new Set(Object.values(OPENERS));

export default function Editor({ value, onChange, lang = "py" }) {
  const [val, setVal] = useState(value || "");
  const taRef = useRef(null);

  useEffect(() => setVal(value || ""), [value]);

  const applyEdit = (next, selStart, selEnd) => {
    setVal(next);
    requestAnimationFrame(() => {
      const el = taRef.current;
      if (!el) return;
      el.selectionStart = selStart;
      el.selectionEnd = selEnd;
      el.focus();
    });
    onChange?.(next);
  };

  const toggleCommentBlock = (start, end) => {
    const mark = lang === "cpp" ? "//" : "#";
    const lineStart = val.lastIndexOf("\n", start - 1) + 1;
    let lineEnd = val.indexOf("\n", end);
    if (lineEnd === -1) lineEnd = val.length;

    const block = val.slice(lineStart, lineEnd);
    const lines = block.split("\n");
    const allCommented = lines.every((l) => /^\s*(#|\/\/)/.test(l));
    const edited = lines
      .map((l) => (allCommented ? l.replace(/^(\s*)(#|\/\/)\s?/, "$1") : l.replace(/^(\s*)/, `$1${mark} `)))
      .join("\n");

    const next = val.slice(0, lineStart) + edited + val.slice(lineEnd);
    applyEdit(next, lineStart, lineStart + edited.length);
  };

  const handleKeyDown = (e) => {
    const el = e.currentTarget;
    const start = el.selectionStart;
    const end = el.selectionEnd;

    // toggle comments
    if (e.metaKey && e.key === "/") {
      e.preventDefault();
      toggleCommentBlock(start, end);
      return;
    }

    // auto-pairs
    if (OPENERS[e.key]) {
      e.preventDefault();
      const open = e.key, close = OPENERS[open];
      const selected = val.slice(start, end);
      const insert = selected ? open + selected + close : open + close;
      const caret = start + 1 + (selected ? selected.length : 0);
      const next = val.slice(0, start) + insert + val.slice(end);
      applyEdit(next, caret, caret);
      return;
    }
    if (CLOSERS.has(e.key) && start === end && val.slice(start, start + 1) === e.key) {
      e.preventDefault();
      applyEdit(val, start + 1, start + 1);
      return;
    }
    if (e.key === "Backspace" && start === end && start > 0) {
      const prev = val[start - 1], nextChar = val[start];
      if (OPENERS[prev] && OPENERS[prev] === nextChar) {
        e.preventDefault();
        const next = val.slice(0, start - 1) + val.slice(start + 1);
        applyEdit(next, start - 1, start - 1);
        return;
      }
    }

    // indent/dedent
    if (e.key === "Tab") {
      e.preventDefault();
      if (start === end) {
        const next = val.slice(0, start) + INDENT + val.slice(end);
        applyEdit(next, start + INDENT_LEN, start + INDENT_LEN);
        return;
      }
      const lineStart = val.lastIndexOf("\n", start - 1) + 1;
      let lineEnd = val.indexOf("\n", end);
      if (lineEnd === -1) lineEnd = val.length;
      const block = val.slice(lineStart, lineEnd);
      const edited = e.shiftKey ? block.replace(/^ {1,4}/gm, "") : block.replace(/^/gm, INDENT);
      const next = val.slice(0, lineStart) + edited + val.slice(lineEnd);
      applyEdit(next, lineStart, lineStart + edited.length);
      return;
    }

    // smart newline (Python)
    if (e.key === "Enter") {
      e.preventDefault();
      const lineStart = val.lastIndexOf("\n", start - 1) + 1;
      const currentLine = val.slice(lineStart, start);
      const baseIndent = (currentLine.match(/^[ \t]*/)?.[0]) || "";
      const extra = (lang === "py" && /:\s*$/.test(currentLine)) ? INDENT : "";
      const insert = "\n" + baseIndent + extra;
      const next = val.slice(0, start) + insert + val.slice(end);
      const caret = start + insert.length;
      applyEdit(next, caret, caret);
      return;
    }

    // backspace eat spaces to previous indent stop
    if (e.key === "Backspace" && start === end) {
      const lineStart = val.lastIndexOf("\n", start - 1) + 1;
      const before = val.slice(lineStart, start);
      if (/^[ \t]*$/.test(before) && before.length > 0) {
        e.preventDefault();
        if (before.endsWith("\t")) {
          const next = val.slice(0, start - 1) + val.slice(end);
          applyEdit(next, start - 1, start - 1);
          return;
        }
        const trailingSpaces = (before.match(/ *$/)?.[0].length) || 0;
        if (trailingSpaces > 0) {
          const del = (trailingSpaces % INDENT_LEN) || INDENT_LEN;
          const newStart = start - del;
          const next = val.slice(0, newStart) + val.slice(start);
          applyEdit(next, newStart, newStart);
          return;
        }
      }
    }
  };

  return (
    <textarea
      ref={taRef}
      className="editor code-input"
      value={val}
      onChange={(e) => {
        setVal(e.target.value);
        onChange?.(e.target.value);
      }}
      onKeyDown={handleKeyDown}
      spellCheck={false}
    />
  );
}
