# Plan — MVP Part Buddy

Status: **M1 zakończone, gotowe do startu M2**.
Estymata: 3-4 tygodnie pracy hobbystycznej.

## Cel MVP

Działająca lokalnie webowa gra trivia ABCD z AI prowadzącym (TTS + szablony), oceniana przez deterministyczny algorytm, obsługująca solo i hotseat. Wystarczająca jako element portfolio.

## Kryteria sukcesu

- [ ] Gra trivia rozgrywa pełną sesję (10 pytań, 15s/pytanie, scoring działa)
- [ ] Push-to-talk poprawnie nagrywa i wysyła audio do Groq Whisper
- [ ] Sędzia poprawnie ocenia: literę ("A"), treść ("Warszawa") i klik
- [ ] AI prowadzący odtwarza pre-generowane komentarze (intro/correct/wrong/outro)
- [ ] Hotseat działa: wybór 2-6 graczy, ranking sesji
- [ ] Pełna sesja kończy się ekranem wyników i zapisem do SQLite
- [ ] Latencja end-to-end (klik → audio response): <3s

## Milestone'y

### M1 — Setup i kościec (2-3 dni)
- [x] Inicjalizacja venv (root) + `requirements.txt` (FastAPI 0.136.1, uvicorn 0.46.0, SQLModel 0.0.38)
- [x] Inicjalizacja Vite + React + TS (`frontend/`, 153 paczek, 0 vulns)
- [x] Hello-world FastAPI + struktura `backend/app/` (`/`, `/health`)
- [x] CORS middleware (allow_origins=`http://localhost:5173`, methods explicit GET/POST/OPTIONS, headers Content-Type/Authorization)
- [x] Pierwszy commit + branch `main` + remote `origin` (https://github.com/mikolaj11111111/Party-Buddy.git)
- [x] **SQLite + przykładowy endpoint z SQLModel** (smoke test ORM, dummy `Ping` model)
- [x] **Konfiguracja Ruff** (`pyproject.toml` z regułami formatowania/lintingu/sortowania importów)
- [x] **Konfiguracja Prettier** (`.prettierrc` w `frontend/`)

### M2 — Sędzia i baza pytań (3-4 dni)
- [x] Schema pytania w JSON (`id`, `category`, `difficulty`, `question`, `options{A..D}`, `correct_answer`, `explanation?`, `aliases?`)
- [ ] `data/questions/<category>.json` — 11 plików per kategoria (geography, popculture, history, movies, music, science, internet_games, sport, technology, language_literature, general). Pierwsza partia: ~180 pytań. Docelowo 600-800 w kolejnych iteracjach.
- [x] Loader pytań z katalogu (zbiera wszystkie kategorie, waliduje schemat, wykrywa duplikaty `id`)
- [x] `core/judge.py`: porównanie litery + matching treści (rapidfuzz)
- [x] Testy jednostkowe sędziego (poprawne, błędne, literówki, wielkość liter, aliasy)
- [ ] Schema odpowiedzi użytkownika dla `POST /api/answer`: request (`question_id`, `answer_letter?`, `answer_text?`, `input_method`) + response (`question_id`, `submitted_answer`, `matched_answer?`, `is_correct`, `correct_answer`, `explanation?`, `score_delta`)
- [ ] Endpoint `POST /api/answer` (input: question_id + answer_text/letter)

### M3 — STT integracja (2-3 dni)
- [ ] `core/stt.py`: klient Groq Whisper API
- [ ] Endpoint `POST /api/stt` (multipart audio → tekst)
- [ ] Frontend: komponent `MicButton` (push-to-talk + MediaRecorder + WAV)
- [ ] E2E: wciśnij mikrofon → wyślij audio → odbierz tekst → wyświetl

### M4 — TTS i komentarze (3-4 dni)
- [ ] Instalacja Piper + polski model głosu
- [ ] `core/tts.py`: wrapper + cache na dysk (hash text+voice → mp3/wav)
- [ ] Słownik szablonów komentarzy (intro, correct x10, wrong x10, partial x5, outro)
- [ ] Skrypt pre-generujący wszystkie szablony do `data/tts_cache/`
- [ ] Endpoint `GET /api/tts?key=...` zwracający audio z cache
- [ ] Frontend: hook `useAudioPlayer`, sekwencjonowanie wypowiedzi

### M5 — Game engine i UI (4-5 dni)
- [ ] `core/game_engine.py`: stan sesji, kolejka pytań, scoring per gracz
- [ ] Modele SQLModel: Question, Session, Score, Profile (jeden model = tabela DB + schema API)
- [ ] WebSocket `/ws/game` (lub SSE) — push pytań, timera, komentarzy
- [ ] React: strony Menu, Setup (wybór liczby graczy + nicki), Game, Results
- [ ] Timer 15s na pytanie, przejścia między pytaniami
- [ ] Ekran wyników z rankingiem hotseat

### M6 — Polish i historia (2-3 dni)
- [ ] Strona historii sesji (lista, daty, top score)
- [ ] Obsługa błędów (Groq down, brak mikrofonu, brak pytań)
- [ ] README z instrukcją uruchomienia (backend + frontend + Piper)
- [ ] Nagranie krótkiego demo-video do portfolio
- [ ] Tag `v0.1.0-mvp`

## Zasady pracy w trakcie MVP

- Każdy milestone na osobnym branchu (`feat/m1-setup`, `feat/m2-judge`, ...)
- PR do `main` po ukończeniu milestone'u + zaliczonych testach
- Aktualizacja `docs/TODO.md` w trakcie (nowe zadania, pomysły)
- Wpisy do `docs/risk.md` przy każdym workaroundzie / tech debcie
- Brak skoków poza MVP — wszystko nowe ląduje w `TODO.md` z tagiem `[post-MVP]`
