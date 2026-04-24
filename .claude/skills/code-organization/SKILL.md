---
name: code-organization
description: Zasady rozdzielania kodu na pliki i moduły. Stosuj przy każdym generowaniu lub refaktorze kodu — zarówno nowy plik, jak i edycja istniejącego. Wymusza jeden obszar odpowiedzialności na plik, cienki entrypoint, separację logiki od I/O i integracji.
---

## Podział na pliki

- Kod obejmujący >1 odpowiedzialność → rozdziel na pliki. Nie pakuj wszystkiego do jednego.
- Jeden plik = jeden główny obszar odpowiedzialności.
- Powiązane klasy / funkcje / modele danych trzymaj razem w tym samym pliku lub module.
- Unikaj dwóch skrajności: jeden megaplik **i** sztuczne rozbijanie na mikropliki po 10 linii.

## Entrypoint

- Plik startowy (`main.py`, `app.py`, `index.ts`, `__main__.py`) jest cienki.
- Entrypoint tylko: parsowanie argów/config, wire-up zależności, wywołanie głównej funkcji.
- Zero logiki biznesowej w entrypoincie.

## Warstwy

- Logika biznesowa osobno od warstwy I/O (HTTP handlers, CLI, DB queries, pliki).
- Endpointy / handlery tylko parsują input, wołają logikę, zwracają response.
- Integracje z zewnętrznymi usługami (API, DB, message broker, storage) w osobnych modułach — jedna integracja = jeden moduł.

## Anty-wzorce

- Zakaz `utils.py` / `helpers.py` / `common.py` jako worków na wszystko. Jeśli funkcja nie pasuje nigdzie → znajdź jej prawdziwy dom albo stwórz moduł z konkretną nazwą (`text_parsing.py`, `date_math.py`).
- Zakaz circular imports — jeśli się pojawiają, zły podział.

## Workflow przy większej funkcjonalności

1. Najpierw zaproponuj strukturę plików (drzewo + 1 zdanie co w każdym).
2. Czekaj na akceptację.
3. Dopiero wtedy pisz kod.

Małe zmiany (1-2 pliki, oczywiste miejsce) — pomiń krok 1, pisz od razu.
