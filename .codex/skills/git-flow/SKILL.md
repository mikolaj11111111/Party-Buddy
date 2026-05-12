---
name: git-flow
description: "Project-local GitHub Flow checklist. Use when a feature or milestone from docs/plan.md is complete and should be committed or pushed."
---

# Git Flow

Use this skill after a feature or milestone from `docs/plan.md` is complete.

## Checklist

1. Check `git status` and review the diff.
2. Verify secrets are not staged: `.env`, API keys, tokens, private data.
3. Run the relevant checks before committing.
4. Stage only the files that belong to the change.
5. Use Conventional Commits in English:
   - `feat: add abcd judge`
   - `fix: handle empty stt response`
   - `docs: update plan after m2`
   - `test: add judge unit tests`
   - `chore: complete m1 setup`
6. Push the current branch to `origin`.
7. Update `docs/plan.md`, `docs/TODO.md`, and `docs/risk.md` only when the change affects them.

## Hard Rules

- Never commit secrets.
- Never force push to `main`.
- Never use `--no-verify` unless the user explicitly asks and the reason is documented.
- Do not mix unrelated work in one commit.
