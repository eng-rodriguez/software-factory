---
name: explore
description: Read-only exploration of a codebase or an unfamiliar area. Use for /explore, onboarding to a new repo, "how does X work", or "where is Y". Writes nothing.
---
Input: a question about the codebase.

1. Run factory:codebase-researcher with the question. For a question spanning several areas or repos (see .factory.yml), run one researcher per area in parallel.
2. Answer the question directly in 5–15 lines, citing file:line for every claim.
3. Add, only when useful: a short call flow (A → B → C), the bounded contexts involved, and gaps such as missing tests or undocumented behavior.
4. End with up to three follow-up questions worth asking next.

Rules: never edit, create or delete files; never run commands that change state; say "not found" rather than guess.
