# Homework 6 - Local AI Chat

This project uses `FastAPI + Vue3` to build a simple chat UI.

The frontend sends messages to `POST /api/chat`.
The backend forwards the request to a local Ollama model.

## Run backend

```powershell
cd homework6\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run frontend

```powershell
cd homework6\frontend
npm install --cache .\.npm-cache
npm run dev
```

## Ollama config

Example `.env`:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:1.5b
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

If the model is missing, pull one first:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen2.5:1.5b
```
