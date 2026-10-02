---
name: principles-design
description: Software design rules from A Philosophy of Software Design and Clean Code, plus the precedence table that resolves conflicts between all principle skills. Use when writing or reviewing any code, naming things, splitting modules, or when two principles disagree.
---

## Rules
1. Prefer deep modules: a simple interface hiding substantial behavior. Flag shallow pass-through classes and functions.
2. Pull complexity downward: the module absorbs edge cases so callers don't.
3. Define errors out of existence where possible (idempotent operations, sensible defaults) before adding exception paths.
4. Comments explain *why* and interface contracts, not *what* the code does.
5. Names are precise and from the domain; a vague name is a design smell.
6. Functions do one thing at one level of abstraction, but never split a function just to make it short.
7. No duplicated knowledge; three similar blocks justify an abstraction, two do not.
8. Tests are first-class code: readable, one behavior per test, builders for setup.

## Review questions
- Which module got more complex for its callers, and could it absorb that complexity instead?
- Is there a class or function whose interface is as complex as its body?
- Would a newcomer understand each name without reading its implementation?
- Does each test name the one behavior it checks?

## Precedence
When principles conflict, every reviewer resolves them the same way:

| Conflict | Winner | Rule |
| --- | --- | --- |
| Small functions (Clean Code) vs deep modules (APOSD) | APOSD for structure, Clean Code for naming and tests | Never add a layer whose interface is as complex as its body |
| Repository pattern (Cosmic Python) vs Django ORM | Django default | Services + selectors; repository only in complex core domains |
| Microservices vs simplicity | Modular monolith | Extract only with an ADR naming the driver |
| Generic CRUD vs DDD aggregates | DDD in core domains | Supporting/generic subdomains may stay plain CRUD |
| Speed vs eval rigor (AI features) | Evals | No eval, no merge |
