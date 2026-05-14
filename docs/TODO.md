# TODO

## Otwarte — MVP

- [ ] Zdecydować, czy zostawić `data/test_questions/` po przejściu loadera i judge na `data/questions/`
- [ ] Limit długości nagrania głosowego (np. 5s — twardy cut)
- [ ] Usunąć tymczasowy endpoint/model `Ping` po dodaniu prawdziwych modeli domenowych

## Pomysły / dyskusja

- [ ] Czy po sesji pokazać statystyki per kategoria pytań
- [ ] Schema odpowiedzi: `is_correct` jest wyliczane przez backend/sędziego i zwracane w response, nie wysyłane przez klienta

## Decyzje do podjęcia (blokujące)

- [ ] **Reguła routowania pytań między kategoriami** dla nakładających się tematów (`popculture` ↔ `movies`/`music`/`internet_games`) — sub­agent zauważył ryzyko

## Post-MVP

- [ ] [post-MVP] Admin UI do edycji pytań (v0.5)
- [ ] [post-MVP] Migracja questions.json → SQLite (v0.5)
- [ ] [post-MVP] Druga gra: 5 sekund lub wisielec (v1)
- [ ] [post-MVP] Wybór głosu z 2-3 opcji (v1)
- [ ] [post-MVP] LLM jako sędzia hybrydowy (fallback dla niepewnych) (v2)
- [ ] [post-MVP] LLM-generowane komentarze kontekstowe (v2)
- [ ] [post-MVP] Embeddingi do synonimów jeśli matching słaby (v2)
- [ ] [post-MVP] Deploy publiczny + auth + Postgres (v3)
- [ ] [post-MVP] Multiplayer online (v4)
- [ ] [post-MVP] Analiza emocji/tonu/twarzy (v5)
- [ ] [post-MVP] Kalambury, gry z gestami (v5)

## Zrobione

- [x] Ustalenie scope MVP
- [x] Wybór stacku
- [x] Decyzja: ABCD zamknięte (nie pytania otwarte)
- [x] Decyzja: jeden globalny profil (bez auth na MVP)
- [x] Decyzja: STT przez Groq API (słaby sprzęt)
- [x] Decyzja: TTS Piper lokalnie
- [x] Decyzja: bez spaCy na MVP (ABCD nie wymaga)
- [x] Decyzja: SQLModel zamiast czystego SQLAlchemy (lepsza integracja z FastAPI)
- [x] Decyzja: dataset pytań w `data/questions/<category>.json` (per kategoria) zamiast jednego pliku
- [x] Utworzenie struktury docs/
- [x] M1: venv, requirements.txt, FastAPI hello-world, CORS, SQLite/SQLModel smoke test, Ruff, Vite React TS, Prettier, git init + remote
- [x] M2: wybrano mały ręczny dataset smoke-testowy i dodano `data/test_questions/geography.json` (10 pytań)
- [x] M2: dodano pierwszy docelowy batch `data/questions/` (geography/history/science, 30 pytań)
- [x] M2: rozszerzono `data/questions/` do pełnej pierwszej partii (11 kategorii, 181 pytań)
- [x] Decyzja: audio z frontendu wysyłamy do STT jako `multipart/form-data`
- [x] M3: STT E2E działa lokalnie (mikrofon → backend → Groq Whisper → tekst w frontendzie)
- [x] Decyzja: Piper używamy przez `piper-tts==1.4.2` i CLI `python -m piper` z forka `OHF-Voice/piper1-gpl`
- [x] Decyzja: cache TTS zostaje w WAV, bez ffmpeg/MP3 na MVP
- [x] Decyzja: TTS pre-generujemy tylko dla komentarzy prowadzącego, nie dla treści pytań
- [x] M4: wygenerowano 27 komentarzy TTS do `data/tts_cache/` z domyślnym głosem `pl_PL-gosia-medium`
- [x] M5: dodano `core/game_engine.py` ze stanem sesji, kolejką pytań, hotseat i scoringiem per gracz
- [x] M5: dodano tabele SQLModel `Question`, `Session`, `Score`, `Profile`
- [x] Decyzja: realtime gry przez jeden dwukierunkowy WebSocket `/ws/game`
- [x] M5: dodano `/ws/game` z `deadline_at` zamiast wysyłania ticków timera
- [x] M5: dodano frontendowe strony Menu, Setup, Game i Results pod `/ws/game`
- [x] M5: dodano 15s timer pytania, 3s intro/outro i 3s przejścia między rundami
- [x] M5: dodano ekran wyników z rankingiem hotseat
- [x] M5: naprawiono polskie znaki w `data/questions/` i dodano test jakości datasetu na utracone markery `?`
- [x] M6: dodano zapis zakończonej sesji do SQLite, endpoint `/api/history/sessions` i stronę historii w UI
- [x] M6: uzupełniono README o uruchomienie backendu, frontendu i lokalny zapis historii
- [x] Decyzja: testy backendu uruchamiamy wyłącznie przez pytest
