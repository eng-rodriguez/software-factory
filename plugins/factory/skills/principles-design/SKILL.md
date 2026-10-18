---
name: principles-design
description: Shared design guidance and applicability rules. Use when designing or reviewing code, or resolving competing factory conventions.
---

## Applicability

Classify guidance before enforcing it:
- **Safeguards:** protect authorization, tenant/data isolation, secrets, compatibility, user work, and truthful verification. Do not waive these to satisfy a convention.
- **Defaults:** prefer these when the project has no established approach. A different approach is not a defect by itself.
- **Conditional patterns:** apply only when the stated problem exists; explain the trigger and tradeoff in the brief.

Resolve competing preferences using the approved requirements and scope, then security/correctness/compatibility constraints, documented project contracts and decisions, applicable stack conventions, and finally factory defaults. Existing code is evidence, not permission to repeat a security defect. Report material conflicts; do not redesign the project to match a book. An exception to a default needs a concise rationale, not a new approval checkpoint unless scope or risk changes.

## Defaults
1. Prefer deep modules: simple interfaces hiding meaningful behavior. Keep thin adapters when they isolate a real external boundary; do not add pass-through layers without a purpose.
2. Absorb implementation complexity inside its owner without hiding failures or policy decisions callers must understand.
3. Eliminate avoidable error cases with explicit invariants and safe defaults; do not silently turn failure into success.
4. Comments explain intent, constraints and contracts. Names use the project's domain language.
5. Keep functions cohesive; do not split them merely to shorten them.
6. Abstract shared knowledge that changes together. Repetition is evidence to investigate, not a numerical threshold requiring abstraction.
7. Test observable behavior with readable setup. One scenario may need several assertions to establish its outcome.

## Review
For each finding cite the applicable safeguard, default or conditional pattern and its concrete impact. Do not block on a preference where an existing project convention is sound. Prefer a modular monolith; introduce service boundaries, repositories, events or other layers only for a demonstrated requirement. Use an ADR for significant lasting tradeoffs, not every local choice.
