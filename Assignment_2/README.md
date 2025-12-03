# Assignment 2: Collaborative Coding Interview Platform (planning)

## Tech choices
- Frontend: React + Vite with Monaco editor (JS/Python highlighting), Socket.IO client.
- Backend: FastAPI + python-socketio (ASGI), Python 3.11 (conda env), `uv` for deps.
- Code execution: JS runner in browser; Python via Pyodide (WASM, browser-only).
- Tooling: `concurrently` for dev (client + backend); pytest/httpx/socketio test client for integration.
- Deploy: Render; containerized with multi-stage Dockerfile (Node for build, `python:3.11-slim` base for runtime).

## Homework answers tracker
- Q1 initial prompt: see next section (copy/paste to homework form).
- Q2 test command: `npm run test` (runs `pytest` in `Assignment_2/server`).
- Q3 npm dev command: `npm run dev` (concurrently Vite + uvicorn).
- Q4 syntax highlighting library: Monaco editor.
- Q5 Python→WASM library: Pyodide.
- Q6 Docker base image: `python:3.11-slim`.
- Q7 deployment service: Render.

## Initial AI prompt (Q1)
Use this prompt to ask AI to scaffold both frontend and backend in one go:

```
You are building a collaborative online coding interview platform. Create both frontend and backend with the following requirements:
- Frontend: React + Vite. Use Monaco editor with syntax highlighting for JavaScript and Python. Support room-based collaborative editing with Socket.IO client. Show real-time updates for all connected users (code content + language selection). Provide UI to create/share a session link, select language, edit code, and run code. Execute JavaScript in-browser in an isolated runner; execute Python in-browser via Pyodide (WASM) only—no server-side code execution. Display output/errors in a console panel.
- Backend: Python FastAPI (ASGI) with python-socketio for realtime. Provide REST/OpenAPI for basic health and session creation if needed. Implement Socket.IO events: join room, code change, language change, optional run request echo. Use CORS for the frontend dev origin. Keep room state in memory for now. Include uvicorn entrypoint.
- Testing: add integration tests to verify client/server interaction (socket events round-trip, REST endpoints) using pytest, httpx, and the socketio test client. Provide npm test scaffolding if minimal.
- Dev workflow: add `concurrently`-based `npm run dev` to start Vite and the FastAPI server together. Document commands in README for setup, run, and tests (conda env + uv for Python deps; npm for frontend).
- Containerization: create a single Dockerfile using multi-stage build (Node to build frontend, python:3.11-slim for backend/runtime). Serve built frontend via FastAPI static or similar. Add Render-friendly start command (uvicorn).
- Deployment: target Render; include any render.yaml/Procfile guidance and environment variable notes.
Deliver the code in `Assignment_2/client` and `Assignment_2/server` folders with clear scripts and instructions.
```

## Environment setup
- Create conda env: `conda create -n ai-interview python=3.11`
- Activate: `conda activate ai-interview`
- Install Python deps (from `Assignment_2/server`): `uv pip install -r requirements.txt`
- Install frontend deps (from `Assignment_2/client`): `npm install`
- Dev server: from `Assignment_2/`, `npm run dev` (starts Vite + uvicorn)
- Tests: from `Assignment_2/`, `npm run test`

## Docker
- Build: `docker build -t coding-interview .`
- Run: `docker run -p 8000:8000 coding-interview`
- The backend serves the built frontend from `server/dist` when present (Docker image does this by default).

## Render
- Example `render.yaml` included for Docker deploy. Make sure CORS origins match your Render URL.

## Notes
- Follow AI Dev Tools Zoomcamp (02-end-to-end) patterns for README commands, dev scripts, testing, Docker, and Render deploy.
- Commit frequently and keep homework answers updated as features land.
