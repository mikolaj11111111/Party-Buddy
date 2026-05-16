# Plan — MVP Part Buddy

Status: **M6 w trakcie — historia sesji zapisywana do SQLite i widoczna w UI**.
Estymata: 3-4 tygodnie pracy hobbystycznej.

## Cel MVP

Działająca lokalnie webowa gra trivia ABCD z AI prowadzącym (TTS + szablony), oceniana przez deterministyczny algorytm, obsługująca solo i hotseat. Wystarczająca jako element portfolio.

## Kryteria sukcesu

- [ ] Gra trivia rozgrywa pełną sesję (10 pytań, 15s/pytanie, scoring działa)
- [x] Push-to-talk poprawnie nagrywa i wysyła audio do Groq Whisper
- [ ] Sędzia poprawnie ocenia: literę ("A"), treść ("Warszawa") i klik
- [x] AI prowadzący odtwarza pre-generowane komentarze (intro/correct/wrong/outro)
- [ ] Hotseat działa: wybór 2-6 graczy, ranking sesji
- [x] Pełna sesja kończy się ekranem wyników i zapisem do SQLite
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
- [x] `data/questions/<category>.json` — 11 plików per kategoria (geography, popculture, history, movies, music, science, internet_games, sport, technology, language_literature, general). Pierwsza partia: ~180 pytań. Docelowo 600-800 w kolejnych iteracjach.
- [x] Loader pytań z katalogu (zbiera wszystkie kategorie, waliduje schemat, wykrywa duplikaty `id`)
- [x] `core/judge.py`: porównanie litery + matching treści (rapidfuzz)
- [x] Testy jednostkowe sędziego (poprawne, błędne, literówki, wielkość liter, aliasy)
- [x] Schema odpowiedzi użytkownika dla `POST /api/answer`: request (`question_id`, `answer_letter?`, `answer_text?`, `input_method`) + response (`question_id`, `submitted_answer`, `matched_answer?`, `is_correct`, `correct_answer`, `explanation?`, `score_delta`)
- [x] Endpoint `POST /api/answer` (input: question_id + answer_text/letter)

### M3 — STT integracja (2-3 dni)
- [x] `core/stt.py`: klient Groq Whisper API
- [x] Endpoint `POST /api/stt` (multipart audio → tekst)
- [x] Frontend: komponent `MicButton` (push-to-talk + MediaRecorder + webm upload)
- [x] E2E: wciśnij mikrofon → wyślij audio → odbierz tekst → wyświetl

### M4 — TTS i komentarze (3-4 dni)
- [x] Instalacja Piper + polski model głosu
- [x] `core/tts.py`: wrapper + cache na dysk (hash text+voice → WAV)
- [x] Słownik szablonów komentarzy (intro, correct x10, wrong x10, partial x5, outro)
- [x] Skrypt pre-generujący wszystkie szablony do `data/tts_cache/`
- [x] Endpoint `GET /api/tts?key=...` zwracający audio z cache
- [x] Frontend: hook `useAudioPlayer`, sekwencjonowanie wypowiedzi

### M5 — Game engine i UI (4-5 dni)
- [x] `core/game_engine.py`: stan sesji, kolejka pytań, scoring per gracz
- [x] Modele SQLModel: Question, Session, Score, Profile (jeden model = tabela DB + schema API)
- [x] WebSocket `/ws/game` — dwukierunkowy push pytań, deadline'u timera i komentarzy
- [x] React: strony Menu, Setup (wybór liczby graczy + nicki), Game, Results
- [x] Timer 15s na pytanie, 3s intro/outro i 3s przejścia między pytaniami
- [x] Ekran wyników z rankingiem hotseat

### M6 — Polish i historia (2-3 dni)
- [x] Strona historii sesji (lista, daty, top score)
- [ ] Obsługa błędów (Groq down, brak mikrofonu, brak pytań)
- [x] README z instrukcją uruchomienia (backend + frontend + Piper)
- [ ] Nagranie krótkiego demo-video do portfolio
- [ ] Tag `v0.1.0-mvp`

### Poprawki
- [x] zaimplementowac ui do animacji: motion, komponenty ui: material ui, state management: zustand (mały slice: przejścia ekranów, MUI theme/przyciski menu, Zustand dla nawigacji)
- [x] dodac wybor gry
- [x] potem kategorii(jesli gra tego wymaga)
- [x] zwiekszyc baze pytań do gry trivia do 660 pytań (60 na kategorię)
- [x] poprawic blad w histori gier, zamiast liczba punktow/liczba pytan jest liczba punktow/liczba punktow

- [x] poprawic sciezki w kodzie - dane do gry trivia powinny byc w data/trivia/questions/, testowe dla trivii w data/trivia/test_questions


### 5 sekund
- [] dodać baze do gry 5 sekund
- [] dodać ui do gry 5 sekund

### Wisielec
- [] dodać baze do gry wisielec
- [] dodać ui do gry wisielec

- [] popracowac nad dzwiekem game mastera

## Zasady pracy w trakcie MVP

- Każdy milestone na osobnym branchu (`feat/m1-setup`, `feat/m2-judge`, ...)
- PR do `main` po ukończeniu milestone'u + zaliczonych testach
- Aktualizacja `docs/TODO.md` w trakcie (nowe zadania, pomysły)
- Wpisy do `docs/risk.md` przy każdym workaroundzie / tech debcie
- Brak skoków poza MVP — wszystko nowe ląduje w `TODO.md` z tagiem `[post-MVP]`
