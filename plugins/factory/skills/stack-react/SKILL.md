---
name: stack-react
description: How we build React + TypeScript frontends - generated API types, TanStack Query, UI states, accessibility, auth and quality commands. Use when writing or reviewing a detected React frontend.
---
Follow [principles-design](../principles-design/SKILL.md) for applicability. These are defaults for a React/TypeScript SPA; preserve an existing React framework's routing, rendering and data-loading model.

- Prefer strict TypeScript. Use the project's authoritative API contract and generator when available; regenerate for changed contracts or stale output. Do not require a DRF backend or add a generator for an unrelated UI change.
- For a new SPA, TanStack Query is a default for remote state and hooks for local state. Preserve existing stores/framework loaders; justify new state dependencies.
- Every data view handles loading, empty, error and permission-denied states.
- Accessibility: semantic elements, labels, keyboard paths; test with Testing Library queries by role.
- No secrets or tokens in client code; auth via httpOnly cookies or the project's documented flow.
- Components are colocated with their tests; pages compose components and own data fetching.
- Run the project's lint, type, component and acceptance checks. ESLint/TypeScript/Vitest/Playwright are supported conventions, not a reason to replace existing tools.
