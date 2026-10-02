---
name: principles-ml
description: ML and LLM system rules from Designing Machine Learning Systems and AI Engineering. Use when building or reviewing any model, prompt, retrieval, agent or evaluation work.
---

## Rules
1. Define the business metric and the offline metric before any model or prompt work.
2. Build the evaluation set and harness first; no prompt or model change merges without an eval run.
3. Version datasets, prompts, models and eval results together.
4. Set latency and cost budgets per request and test against them.
5. Start with the simplest baseline (rules, retrieval, a smaller model) and beat it with evidence.
6. Guardrails on inputs and outputs: PII handling, prompt-injection defenses, structured output validation.
7. Monitor in production: data drift, quality signals, cost, and a human feedback path.
8. Treat model output as untrusted input: validate it before it reaches the database, a shell, or another user.

## Review questions
- Which eval run shows this change beats the current version, and on which metric?
- What is the per-request latency and cost, and where is it tested?
- How does a malicious document or user message change what the model does?
- How will we know in production that quality dropped?

## Precedence
See principles-design → Precedence when a rule here conflicts with another book. Speed vs eval rigor: evals win.
