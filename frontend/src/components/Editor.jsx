import { useEffect, useRef, useState } from "react";

const INDENT = "    ";
const INDENT_LEN = INDENT.length;

export default function Editor({ value, onChange }) {
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

  const handleKeyDown = (e) => {
    const el = e.currentTarget;
    const start = el.selectionStart;
    const end = el.selectionEnd;

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
      const edited = e.shiftKey
        ? block.replace(/^ {1,4}/gm, "")
        : block.replace(/^/gm, INDENT);

      const next = val.slice(0, lineStart) + edited + val.slice(lineEnd);
      applyEdit(next, lineStart, lineStart + edited.length);
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      const lineStart = val.lastIndexOf("\n", start - 1) + 1;
      const currentLine = val.slice(lineStart, start);
      const baseIndent = (currentLine.match(/^[ \t]*/)?.[0]) || "";
      const extra = /:\s*$/.test(currentLine) ? INDENT : "";
      const insert = "\n" + baseIndent + extra;
      const next = val.slice(0, start) + insert + val.slice(end);
      const caret = start + insert.length;
      applyEdit(next, caret, caret);
      return;
    }

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
          const next =
            val.slice(0, newStart) +
            val.slice(start);
          applyEdit(next, newStart, newStart);
          return;
        }
      }
    }
  };

  return (
    <textarea
      ref={taRef}
      className="editor"
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
