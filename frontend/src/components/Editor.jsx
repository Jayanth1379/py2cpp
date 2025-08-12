import { useState, useEffect } from "react";

export default function Editor({ value, onChange }) {
  const [val, setVal] = useState(value || "");
  useEffect(()=>setVal(value),[value]);
  return (
    <textarea className="editor" value={val}
      onChange={(e)=>{ setVal(e.target.value); onChange?.(e.target.value); }}
      spellCheck={false} />
  );
}
