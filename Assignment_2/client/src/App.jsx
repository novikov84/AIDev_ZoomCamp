import { useEffect, useMemo, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import { io } from "socket.io-client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [sessionId, setSessionId] = useState(
    new URLSearchParams(window.location.search).get("room") || ""
  );
  const [code, setCode] = useState("// Start coding\n");
  const [language, setLanguage] = useState("javascript");
  const [output, setOutput] = useState("Ready.");
  const [pyLoading, setPyLoading] = useState(false);
  const socketRef = useRef(null);
  const pyodideRef = useRef(null);

  // Build socket only once
  useEffect(() => {
    const socket = io(API_URL, {
      transports: ["websocket", "polling"],
      autoConnect: false
    });
    socketRef.current = socket;
    socket.on("connect_error", (err) => {
      setOutput(`Socket error: ${err.message}`);
    });
    socket.on("state_sync", (state) => {
      if (state?.code !== undefined) setCode(state.code);
      if (state?.language) setLanguage(state.language);
    });
    socket.on("code_update", (payload) => {
      if (payload?.code !== undefined) setCode(payload.code);
    });
    socket.on("language_update", (payload) => {
      if (payload?.language) setLanguage(payload.language);
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  // Join room when sessionId present
  useEffect(() => {
    const socket = socketRef.current;
    if (!socket || !sessionId) return;
    if (!socket.connected) socket.connect();
    socket.emit("join", { room: sessionId });
    const url = new URL(window.location.href);
    url.searchParams.set("room", sessionId);
    window.history.replaceState({}, "", url.toString());
  }, [sessionId]);

  const createSession = async () => {
    try {
      const res = await fetch(`${API_URL}/api/session`, { method: "POST" });
      const data = await res.json();
      if (data.sessionId) {
        setSessionId(data.sessionId);
        setOutput(`Session created: ${data.sessionId}`);
      }
    } catch (err) {
      setOutput(`Failed to create session: ${err.message}`);
    }
  };

  const shareLink = useMemo(() => {
    const url = new URL(window.location.href);
    if (sessionId) url.searchParams.set("room", sessionId);
    return url.toString();
  }, [sessionId]);

  const onCodeChange = (value) => {
    setCode(value || "");
    if (socketRef.current && sessionId) {
      socketRef.current.emit("code_change", { room: sessionId, code: value || "" });
    }
  };

  const onLanguageChange = (value) => {
    setLanguage(value);
    if (socketRef.current && sessionId) {
      socketRef.current.emit("language_change", { room: sessionId, language: value });
    }
  };

  const ensurePyodide = async () => {
    if (pyodideRef.current) return pyodideRef.current;
    setPyLoading(true);
    if (!window.loadPyodide) {
      await import("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");
    }
    const pyodide = await window.loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
    });
    pyodideRef.current = pyodide;
    setPyLoading(false);
    return pyodide;
  };

  const runJs = () => {
    try {
      // eslint-disable-next-line no-new-func
      const result = new Function(code)();
      setOutput(String(result ?? "done"));
    } catch (err) {
      setOutput(`JS error: ${err.message}`);
    }
  };

  const runPython = async () => {
    try {
      const pyodide = await ensurePyodide();
      const result = await pyodide.runPythonAsync(code);
      setOutput(String(result ?? "done"));
    } catch (err) {
      setOutput(`Python error: ${err.message}`);
    }
  };

  return (
    <div className="app">
      <div className="header">
        <div>
          <h2 style={{ margin: 0 }}>Live Coding Interview</h2>
          <p style={{ margin: "4px 0 0" }}>
            FastAPI + Socket.IO backend, Monaco editor, browser-only execution.
          </p>
        </div>
        <div className="controls">
          <button onClick={createSession}>Create session</button>
          <input
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="Session ID"
          />
          <button
            className="secondary"
            onClick={() => navigator.clipboard?.writeText(shareLink)}
            disabled={!sessionId}
          >
            Copy link
          </button>
          <select value={language} onChange={(e) => onLanguageChange(e.target.value)}>
            <option value="javascript">JavaScript</option>
            <option value="python">Python</option>
          </select>
          <button onClick={language === "python" ? runPython : runJs} disabled={!sessionId}>
            Run {language}
          </button>
          {pyLoading && <span>Loading Pyodide…</span>}
        </div>
      </div>

      <div className="editor-grid">
        <div className="panel">
          <h3>Editor</h3>
          <Editor
            height="65vh"
            theme="vs-light"
            language={language === "python" ? "python" : "javascript"}
            value={code}
            onChange={onCodeChange}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              wordWrap: "on"
            }}
          />
        </div>
        <div className="panel">
          <h3>Console</h3>
          <div className="console">{output}</div>
          <div style={{ marginTop: "0.75rem" }}>
            <div style={{ fontSize: "0.9rem", color: "#475569" }}>Share link</div>
            <code style={{ fontSize: "0.85rem", wordBreak: "break-all" }}>{shareLink}</code>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
