# TODO

## Otwarte — MVP

- [ ] Rozszerzyć docelowy dataset `data/questions/` z 3 kategorii do pełnej pierwszej partii M2
- [ ] Zdecydować, czy zostawić `data/test_questions/` po przejściu loadera i judge na `data/questions/`
- [ ] Wybór konkretnego polskiego głosu Piper (porównać `pl_PL-darkman-medium`, `pl_PL-gosia-medium`)
- [ ] Decyzja: mp3 vs wav w cache TTS (wav prostszy, mp3 mniejszy)
- [ ] Decyzja: WebSocket vs SSE dla push'u stanu gry (SSE prostszy jeśli komunikacja jednokierunkowa)
- [ ] Format multipart vs base64 dla audio z frontendu
- [ ] Limit długości nagrania głosowego (np. 5s — twardy cut)
- [ ] Usunąć tymczasowy endpoint/model `Ping` po dodaniu prawdziwych modeli domenowych

## Pomysły / dyskusja

- [ ] Czy pre-generować TTS dla wszystkich tekstów pytań (mała baza = OK), czy tylko komentarzy
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
- [x] Decyzja: testy backendu uruchamiamy wyłącznie przez pytest
