# Party Buddy

Webowa platforma imprezowych gier z AI prowadzącym.

**Status:** wczesny development, M6 rozpoczęte; historia sesji zapisuje wyniki do SQLite i ma ekran w UI.

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
- `.codex/skills/` — lokalne skille projektu

## Uruchomienie

Backend:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Frontend uruchom w drugim terminalu:

```powershell
cd frontend
npm.cmd run dev
```

STT wymaga zmiennej w `.env`:

```env
GROQ_WHISPER_API=...
```

TTS używa Piper (`piper-tts==1.4.2`) i domyślnego głosu `pl_PL-gosia-medium`.
Modele głosu trzymaj lokalnie w `data/voices/`, a cache audio w `data/tts_cache/`.

Pobranie głosów:

```powershell
.\venv\Scripts\python.exe -m piper.download_voices --download-dir data\voices pl_PL-gosia-medium pl_PL-darkman-medium
```

Pregeneracja komentarzy:

```powershell
.\venv\Scripts\python.exe scripts\pregenerate_tts.py
```

Historia zakończonych sesji zapisuje się lokalnie w `data/part_buddy.db`.

## Quality checks

Backend:

```powershell
.\venv\Scripts\python.exe -m ruff check backend
.\venv\Scripts\python.exe -m ruff format --check backend
.\venv\Scripts\python.exe -m pytest
```

Frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run format:check
npm.cmd run build
```

## Licencja

Projekt prywatny / portfolio.
