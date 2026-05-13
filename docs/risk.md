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

## Stare regulaminy w `.claude/rules/rules.md`
- **Lokalizacja:** `.claude/rules/rules.md`
- **Problem:** Plik zawierał nieaktualne info (desktop-first, spaCy obowiązkowo, AI tylko prowadzi/komentuje). Aktualne decyzje: web-only, bez spaCy na MVP, ABCD zamknięte.
- **Wpływ:** średni — agent mógł postępować zgodnie z nieaktualnymi rules przy braku jasnego kontekstu.
- **Propozycja:** przenieść aktualne reguły do `AGENTS.md`, a lokalne skille do `.codex/skills/`.
- **Status:** fixed (2026-05-12, `.claude/` zastąpione przez `AGENTS.md` + `.codex/skills/`)

## Subagent Write blocked
- **Lokalizacja:** stare uprawnienia Claude Code (settings)
- **Problem:** Subagenci `general-purpose` nie mogli używać `Write` na `data/questions/*.json` mimo że parent mógł.
- **Wpływ:** niski — projekt przeszedł na lokalne skille/rules dla Codex; dataset M2 zacznie się od małego ręcznego smoke-testu.
- **Propozycja:** nie wracać do `.claude/settings.json`; jeśli pełny dataset będzie generowany agentowo, zrobić to etapami w aktualnym workflow.
- **Status:** fixed (2026-05-12, migracja z `.claude/` do `AGENTS.md` + `.codex/skills/`)

## Licencja Open Trivia DB
- **Lokalizacja:** `data/questions/SOURCES.md`
- **Problem:** Pierwszy batch pytań bazuje na Open Trivia DB, które deklaruje CC BY-SA 4.0.
- **Wpływ:** średni — publiczne użycie datasetu może wymagać atrybucji i zgodności z warunkami ShareAlike.
- **Propozycja:** trzymać źródła w `SOURCES.md`; przed publikacją portfolio zdecydować, czy zostawić ten dataset, czy zastąpić pytaniami autorskimi.
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
- **Propozycja:** test w M4. Fallback: ElevenLabs free tier do pre-generacji (nie real-time).
- **Status:** planned (test w M4)

### Latencja end-to-end
- **Lokalizacja:** architektura ogólna
- **Problem:** Cykl audio → upload → Groq → match → TTS → playback realnie 1.5-3s.
- **Wpływ:** średni — granica akceptowalności UX.
- **Propozycja:** UI musi pokazywać stan ("słucham...", "myślę..."). Cache TTS rozwiązuje większość. Pomiar w M5.
- **Status:** planned
