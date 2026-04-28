# Party Buddy

Webowa platforma imprezowych gier z AI prowadzącym.

**Status:** wczesny development, M1 zakończone (setup i kościec).

## Stack MVP

- Backend: Python 3.11 + FastAPI + SQLite
- Frontend: React + Vite + TypeScript
- STT: Groq Whisper API
- TTS: Piper (lokalnie)

## Struktura repo

- `backend/` — FastAPI app
- `frontend/` — React + Vite SPA
- `data/` — pytania, baza SQLite, cache TTS (poza repo)
- `docs/` — plan, TODO, ryzyka, decyzje
- `AGENTS.md` — kontekst projektu dla agentów kodujących

## Uruchomienie

Backend:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm.cmd run dev
```

## Quality checks

Backend:

```powershell
.\venv\Scripts\python.exe -m ruff check backend
.\venv\Scripts\python.exe -m ruff format --check backend
```

Frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run format:check
```

## Licencja

Projekt prywatny / portfolio.
