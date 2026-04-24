---
name: git-flow
description: Po ukończeniu każdego feature/milestone z docs/plan.md zcommituj i pushnij zmiany na GitHub. Stosuj zawsze gdy feature uznany za zrobiony.
---

## Trigger

Po ukończeniu **każdego feature lub milestone** z `docs/plan.md` (oznaczenie `[x]` w checkliście).

## Kroki

1. **Sprawdź sekrety.** `.env`, klucze API, tokeny, dane prywatne — NIGDY w commicie. Sprawdź `git status` i `git diff --staged` przed commitem.
2. **Stage konkretnie.** `git add <plik>` lub `git add <katalog>`. Bez `git add -A` ani `git add .` — żeby nie wciągnąć przypadkowo niechcianych plików.
3. **Commit.** Conventional Commits po angielsku, krótki opis w trybie rozkazującym:
   - `feat: add ABCD judge with rapidfuzz matching`
   - `fix: handle empty STT response`
   - `refactor: split game_engine into rounds and scoring`
   - `docs: update plan.md after M2 completion`
   - `test: add judge unit tests`
   - `chore: bump fastapi to 0.137.0`
4. **Push.** `git push origin <current-branch>`.
5. **Aktualizuj `docs/plan.md` i `docs/TODO.md`** jeśli featurea zmieniają stan zadań.

## Zakazy

- Nigdy `--no-verify` (nie pomijaj hooków).
- Nigdy force push do `main`.
- Nigdy commit przy nieusuniętych sekretach.
- Nigdy `git add -A` w tym projekcie.

## Granularność

- Mały feature (1-2 pliki, jedna zmiana logiczna) = jeden commit.
- Duży milestone = kilka commitów (np. M2: `feat: judge module`, `test: judge tests`, `docs: update plan after M2`).
