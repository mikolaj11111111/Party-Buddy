---
name: technology-choice-gate
description: "Project-local approval gate for adding or installing dependencies, libraries, frameworks, services, tools, runtimes, SDKs, models, databases, or other technologies. Use before proposing, adding to manifests, installing, importing, or wiring any new technology in this repo."
---

# Technology Choice Gate

Use this skill before any new dependency or technology enters the project.

## Hard Rule

Do not install, add to `requirements.txt`/`package.json`, import, configure, or wire a new technology until the user explicitly accepts it.

## Required Discussion

Before implementation, explain:

1. What problem the technology solves in this exact task.
2. Whether the current stack or standard library can solve it without adding anything.
3. The best no-new-dependency alternative.
4. The best dependency-based option.
5. Tradeoffs: complexity, maintenance, security, testability, size, runtime cost, and MVP fit.
6. What files would change if accepted.

## Questions To Ask

Ask direct questions tailored to the task, at minimum:

- Do we accept adding this dependency/technology now, or prefer the no-new-dependency path?
- Is this meant to be MVP code, dev-only tooling, or a temporary workaround?
- Are there constraints around license, offline use, cost, performance, or Windows support?

## If User Accepts

Proceed with the smallest implementation that fits the accepted option. Update docs only if the choice becomes a lasting project decision.

## If User Rejects

Use the no-new-dependency path or redesign the feature within the existing stack.
