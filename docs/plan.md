# Plan — MVP Part Buddy

Status: **planowanie zakończone, przed startem implementacji**.
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
- [ ] Inicjalizacja venv backend, `requirements.txt`
- [ ] Inicjalizacja Vite + React + TS
- [ ] Hello-world FastAPI + SQLite + przykładowy endpoint
- [ ] CORS, struktura `backend/app/`, `frontend/src/`
- [ ] Konfiguracja Ruff i Prettier
- [ ] Pierwszy commit, gałąź `main`

### M2 — Sędzia i baza pytań (3-4 dni)
- [ ] Schema pytania w JSON (id, kategoria, treść, opcje ABCD, poprawna, aliasy treści)
- [ ] `data/questions.json` z 30-50 pytaniami startowymi
- [ ] `core/judge.py`: porównanie litery + matching treści (rapidfuzz)
- [ ] Testy jednostkowe sędziego (poprawne, błędne, literówki, wielkość liter)
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
