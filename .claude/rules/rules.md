# Rules

## Scope i priorytety
- Trzymaj się aktualnego scope i MVP.
- Preferuj najprostsze rozwiązanie, które działa.
- Jeśli coś wykracza poza MVP, oznacz to jasno i nie implementuj bez potrzeby.
- Kwestionuj decyzje, które zwiększają koszt, złożoność albo czas dowiezienia.

## Styl pracy
- Pisz krótko, konkretnie i bez lania wody.
- Przy większych zmianach najpierw pokaż proponowaną strukturę lub plan, potem implementację.
- Nie wprowadzaj dużych zmian architektonicznych bez jasnego uzasadnienia.
- Nie dodawaj zależności, jeśli nie są wyraźnie potrzebne.

## Organizacja kodu
- Preferuj kilka małych, czytelnych plików zamiast jednego dużego.
- Jeden plik = jedna główna odpowiedzialność.
- Nie trzymaj logiki biznesowej w endpointach, kontrolerach ani UI.
- Integracje z zewnętrznymi usługami trzymaj w osobnych modułach.
- Unikaj plików typu `utils.py`, `helpers.py`, `misc.py` jako worka na wszystko.
- Pliki startowe mają być cienkie.
- Jeśli funkcjonalność robi się zbyt duża, zaproponuj podział na moduły.

## Kontekst projektu
- Projekt to webowa platforma imprezowych gier z AI w roli prowadzącego.
- MVP: polski, **web-only**, lokalne uruchamianie, niskokosztowe, portfolio-first.
- Grupa docelowa: młodzież.
- Pierwsza i jedyna gra w MVP: **trivia ABCD** (zamknięte, 4 opcje, 10 rund/sesja, 15 sek/pytanie).
- Jedna sesja = jedna gra.
- Tryby: solo + hotseat lokalny (kilku graczy, jedno urządzenie, jeden globalny profil).
- Wejście: klik + push-to-talk (głos rozpoznaje literę "A/B/C/D" lub treść odpowiedzi).
- Ocena odpowiedzi: algorytm deterministyczny (porównanie litery + matching treści przez `rapidfuzz`).
- AI w MVP: predefiniowane szablony komentarzy + pre-generowane TTS z dysku. Bez LLM.
- Poza MVP: LLM (sędzia/komentarze), spaCy/embeddingi/RAG, ElevenLabs, wybór głosów, pytania otwarte, multiplayer online, auth, VAD, emocje, kamera, gesty, inne gry, deploy publiczny, desktop app.

## Stack MVP
- Backend: Python 3.11+ w venv, FastAPI, SQLModel.
- Frontend: React + Vite + TypeScript.
- Baza: SQLite (`data/partbuddy.db`).
- STT: **Groq Whisper API** (tani, słaby sprzęt OK).
- TTS: **Piper lokalnie**, polski głos, cache na dysk (`data/tts_cache/`).
- Matching: `rapidfuzz` + stdlib. **Bez spaCy na MVP** — ABCD nie wymaga lematyzacji. spaCy wraca dopiero przy pytaniach otwartych (v2).
- Baza pytań: `data/questions.json` na MVP, migracja do SQLite + admin UI w v0.5.
- Bez LLM API, bez RAG, bez bazy wektorowej, bez embeddingów, bez ElevenLabs, bez Postgres, bez Docker na MVP.

## Dokumentacja
- Aktualizuj dokumentację tylko wtedy, gdy zaszła realna zmiana.
- `CLAUDE.md` aktualizuj tylko przy trwałych zmianach projektowych.
- Do bieżących zmian używaj `docs/TODO.md`, `docs/plan.md`, `docs/risk.md`.
- Ważne decyzje zapisuj w `DECISIONS.md`.
- Istotne zmiany architektury zapisuj w `ARCHITECTURE.md`.
