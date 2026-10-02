---
name: stack-react
description: How we build React + TypeScript frontends - generated API types, TanStack Query, UI states, accessibility, auth and quality commands. Use when writing or reviewing frontend code.
---
- TypeScript strict. API types generated from the DRF OpenAPI schema (`openapi-typescript` or Orval); never hand-write response types.
- Server state with TanStack Query; local state with hooks; no global store unless the brief justifies it.
- Every data view handles loading, empty, error and permission-denied states.
- Accessibility: semantic elements, labels, keyboard paths; test with Testing Library queries by role.
- No secrets or tokens in client code; auth via httpOnly cookies or the project's documented flow.
- Components are colocated with their tests; pages compose components and own data fetching.
- Quality: `eslint`, `tsc --noEmit`, `vitest run`, Playwright for acceptance tests.
