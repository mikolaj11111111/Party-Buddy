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
- **Problem:** Plik zawiera nieaktualne info (desktop-first, spaCy obowiązkowo, AI tylko prowadzi/komentuje). Aktualne decyzje: web-only, bez spaCy na MVP, ABCD zamknięte.
- **Wpływ:** średni — Claude może postępować zgodnie z nieaktualnymi rules przy braku jasnego kontekstu.
- **Propozycja:** zsynchronizować `rules.md` z `CLAUDE.md` lub usunąć duplikujące sekcje.
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
