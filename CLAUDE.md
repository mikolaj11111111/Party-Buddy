# Part Buddy — kontekst projektu

Webowa platforma imprezowych gier z AI w roli prowadzącego (game master).
MVP: portfolio-first, lokalne, niskokosztowe, polski język.

## Aktualny scope MVP

- Jedna gra: trivia ABCD
- Tryby: solo + hotseat lokalny (kilku graczy, jedno urządzenie, jeden globalny profil)
- 10 rund / sesja, 4 odpowiedzi (ABCD), 15 sekund na odpowiedź
- Punkty tylko za poprawność (nie za szybkość)
- Wejście: klik myszą + push-to-talk (głos rozpoznaje literę "A/B/C/D" lub treść odpowiedzi)
- AI prowadzący: predefiniowane szablony komentarzy + pre-generowane TTS z dysku
- Sędzia: deterministyczny algorytm (porównanie litery + matching treści przez `rapidfuzz`)
- Baza pytań: `data/questions/<category>.json` (jeden plik na kategorię — `geography.json`, `history.json`, ...) na MVP. Migracja do SQLite + admin UI w v0.5.
- Historia: jeden globalny profil w SQLite

## Stack

- **Backend:** Python 3.11+ (venv), FastAPI, SQLModel, SQLite
- **Frontend:** React + Vite + TypeScript
- **STT:** Groq Whisper API (tani, słaby sprzęt OK)
- **TTS:** Piper lokalnie (darmowy, offline, polski głos)
- **Matching:** `rapidfuzz` + stdlib (bez spaCy na MVP — ABCD nie wymaga lematyzacji)
- **Audio cache:** `data/tts_cache/`, klucz = hash(tekst + voice_id)
- **Realtime:** WebSocket lub SSE (wybór per endpoint)

## Świadomie poza MVP

- LLM (komentarze i ocenianie)
- spaCy, embeddingi, baza wektorowa, RAG
- ElevenLabs, wybór głosów
- Pytania otwarte (tylko ABCD)
- Multiplayer online, auth, konta email
- VAD, streaming STT
- Analiza emocji / twarzy / tonu
- Inne gry niż trivia (5 sekund, wisielec, państwa-miasta, czółko, kalambury)
- Desktop app, Electron
- Deploy publiczny

## Konwencje techniczne

- Python: venv obowiązkowo, Ruff (format + lint + import sort)
- TS/React: Prettier
- Nazwy w kodzie po angielsku (zmienne, funkcje, klasy, komentarze)
- Komunikacja z użytkownikiem po polsku
- Pliki sekretów (`.env`, klucze API) NIGDY do commita
- Conventional Commits po angielsku (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`)

## Workflow

- GitHub Flow: `main` zawsze stabilny, każda zmiana na osobnym branchu (`feat/`, `fix/`)
- Plan przed dużymi zmianami → akceptacja → implementacja
- Testy przed commitem
- `docs/plan.md`, `docs/TODO.md`, `docs/risk.md` — pliki robocze, **commitowane** do repo

## Architektura modułów (planowana)

```
backend/app/
  main.py              # FastAPI entrypoint (cienki)
  api/                 # endpointy HTTP/WS — tylko parsowanie i delegacja
  core/
    judge.py           # ocena odpowiedzi ABCD + treść
    stt.py             # Groq Whisper integration
    tts.py             # Piper wrapper + cache
    game_engine.py     # stan gry, scoring, runda
  models/              # SQLModel: Question, Session, Score, Profile (modele DB + walidacja API)
  db.py                # SQLite init
```

Logika biznesowa nigdy w endpointach. Integracje (STT/TTS/DB) w osobnych modułach.

## Roadmapa

- **MVP** — opisany wyżej (3-4 tyg)
- **v0.5** — admin UI dla bazy pytań, migracja JSON → SQLite
- **v1** — druga gra (5 sekund lub wisielec), wybór głosu (2-3 opcje)
- **v2** — opcjonalny LLM layer (sędzia hybrydowy, dynamiczne komentarze), embeddingi przy słabym matchingu
- **v3** — deploy publiczny + auth + monetyzacja (jeśli potencjał)
- **v4** — multiplayer online
- **v5** — emocje/ton, kalambury, gesty
