import { useEffect, useMemo, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import { io } from "socket.io-client";

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

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
    const logs = [];
    const originalConsole = window.console;
    // Capture console output while still emitting to the real console
    const patchedConsole = {
      ...originalConsole,
      log: (...args) => {
        logs.push(args.map((x) => String(x)).join(" "));
        originalConsole.log(...args);
      }
    };
    try {
      // eslint-disable-next-line no-global-assign
      console = patchedConsole;
      // eslint-disable-next-line no-new-func
      const result = new Function(code)();
      const resultText = result !== undefined ? String(result) : "";
      const combined = [...logs, resultText || "done"].filter(Boolean).join("\n");
      setOutput(combined);
    } catch (err) {
      setOutput(`JS error: ${err.message}`);
    } finally {
      // eslint-disable-next-line no-global-assign
      console = originalConsole;
    }
  };

  const runPython = async () => {
    try {
      const pyodide = await ensurePyodide();
      let buf = "";
      const capture = { batched: (s) => { buf += s; } };
      pyodide.setStdout(capture);
      pyodide.setStderr(capture);
      const result = await pyodide.runPythonAsync(code);
      const resultText = result !== undefined ? String(result) : "";
      const combined = [buf.trim(), resultText || "done"].filter(Boolean).join("\n");
      setOutput(combined);
    } catch (err) {
      setOutput(`Python error: ${err.message}`);
    } finally {
      if (pyodideRef.current) {
        pyodideRef.current.setStdout();
        pyodideRef.current.setStderr();
      }
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
