---
name: code-organization
description: "Project-local rules for splitting code into files and modules. Use whenever adding or refactoring code in this repo."
---

# Code Organization

Use this skill when adding or refactoring backend or frontend code.

## Rules

- One file should have one main responsibility.
- Keep entrypoints thin: wire dependencies, configure the app, and delegate.
- Do not put business logic in HTTP endpoints, UI components, or startup files.
- Keep external integrations in dedicated modules: one integration, one module.
- Avoid catch-all files like `utils.py`, `helpers.py`, `common.py`, or `misc.py`.
- Split code when a file starts mixing domain logic, I/O, persistence, and integration details.
- Do not split into tiny artificial files if the code is still easier to read together.

## Larger Changes

For larger features, propose the file/module structure first:

```text
path/to/file.py - what it owns
path/to/other.py - what it owns
```

Small obvious changes can be implemented directly.
