# Risk log

Tech debt, ryzyka i workaroundy. Format wpisu:

```
## [krótki tytuł]
- **Lokalizacja:** plik:linia (lub "architektura ogólna")
- **Problem:** opis
- **Wpływ:** niski / średni / wysoki
- **Propozycja:** jak naprawić
- **Status:** open / planned / fixed
```

---

## Stare regulaminy po migracji do `AGENTS.md`
- **Lokalizacja:** historyczny ruleset sprzed migracji; aktualne reguły są w `AGENTS.md`
- **Problem:** Plik zawierał nieaktualne info (desktop-first, spaCy obowiązkowo, AI tylko prowadzi/komentuje). Aktualne decyzje: web-only, bez spaCy na MVP, ABCD zamknięte.
- **Wpływ:** średni — agent mógł postępować zgodnie z nieaktualnymi rules przy braku jasnego kontekstu.
- **Propozycja:** trzymać aktualne reguły w `AGENTS.md`, a lokalne skille w `.codex/skills/`.
- **Status:** fixed (2026-05-12, rules przeniesione do `AGENTS.md` + `.codex/skills/`)

## Subagent Write blocked
- **Lokalizacja:** historyczne ustawienia poprzedniego narzędzia
- **Problem:** Subagenci `general-purpose` nie mogli używać `Write` na `data/questions/*.json` mimo że parent mógł.
- **Wpływ:** niski — projekt przeszedł na lokalne skille/rules dla Codex; dataset M2 zacznie się od małego ręcznego smoke-testu.
- **Propozycja:** jeśli pełny dataset będzie generowany agentowo, robić to etapami w aktualnym workflow.
- **Status:** fixed (2026-05-12, migracja do `AGENTS.md` + `.codex/skills/`)

## Licencja Open Trivia DB
- **Lokalizacja:** `data/questions/SOURCES.md`
- **Problem:** Pierwszy batch pytań bazuje na Open Trivia DB, które deklaruje CC BY-SA 4.0.
- **Wpływ:** średni — publiczne użycie datasetu może wymagać atrybucji i zgodności z warunkami ShareAlike.
- **Propozycja:** trzymać źródła w `SOURCES.md`; przed publikacją portfolio zdecydować, czy zostawić ten dataset, czy zastąpić pytaniami autorskimi.
- **Status:** open

## Licencja Piper GPL-3.0
- **Lokalizacja:** `requirements.txt`, `backend/app/core/tts.py`
- **Problem:** `piper-tts==1.4.2` wskazuje na fork `OHF-Voice/piper1-gpl` z licencją GPL-3.0-or-later.
- **Wpływ:** średni — prywatne/lokalne portfolio jest OK, ale publiczna dystrybucja produktu wymaga ponownej analizy licencji.
- **Propozycja:** przed publicznym releasem zdecydować, czy zostawić Piper, czy przejść na inną TTS opcję/licencję.
- **Status:** open

## Sesja gry WebSocket tylko w pamięci
- **Lokalizacja:** `backend/app/core/game_realtime.py`
- **Problem:** Aktywna sesja gry żyje tylko w jednym połączeniu WebSocket; odświeżenie strony lub rozłączenie resetuje bieżącą rozgrywkę.
- **Wpływ:** niski w lokalnym MVP, średni przy późniejszym multiplayer/reconnect.
- **Propozycja:** w MVP zapisać wynik końcowy do SQLite; reconnect i odtwarzanie aktywnej sesji zostawić poza MVP albo na v0.5+.
- **Status:** open

---

## Ryzyka znane (do monitorowania w trakcie MVP)

### Jakość STT na polski (głos młodzieży, slang, szum)
- **Lokalizacja:** architektura ogólna (`core/stt.py`)
- **Problem:** Groq Whisper może mieć WER >15% na nagraniach z hałasem / akcentem.
- **Wpływ:** wysoki — bezpośrednio rzutuje na UX gry głosowej.
- **Propozycja:** zawsze pokazywać rozpoznany tekst + przycisk "popraw ręcznie". Pomiar WER na 20 testowych nagraniach przed M5.
- **Status:** planned (test w M3)

### Jakość polskich głosów Piper
- **Lokalizacja:** `core/tts.py`
- **Problem:** Piper polski może brzmieć robotycznie. Może być za słabe na "AI prowadzącego".
- **Wpływ:** średni — wpływa na odbiór emocjonalny gry.
- **Propozycja:** odsłuchać próbki `pl_PL-gosia-medium` i `pl_PL-darkman-medium`; fallback: ElevenLabs free tier do pre-generacji (nie real-time).
- **Status:** open (próbki wygenerowane w M4)

### Latencja end-to-end
- **Lokalizacja:** architektura ogólna
- **Problem:** Cykl audio → upload → Groq → match → TTS → playback realnie 1.5-3s.
- **Wpływ:** średni — granica akceptowalności UX.
- **Propozycja:** UI musi pokazywać stan ("słucham...", "myślę..."). Cache TTS rozwiązuje większość. Pomiar w M5.
- **Status:** planned
