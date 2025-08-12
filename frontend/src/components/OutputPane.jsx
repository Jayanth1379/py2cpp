export default function OutputPane({ title, text }) {
  return (
    <div className="pane">
      <h3>{title}</h3>
      <pre className="output">{text || ""}</pre>
    </div>
  );
}
