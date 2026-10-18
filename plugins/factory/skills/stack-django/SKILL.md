---
name: stack-django
description: How we build Django/DRF backends - app layout, thin views, services and selectors, permissions, Celery, tests, settings and quality commands. Use when writing or reviewing a detected Django/DRF backend.
---
Follow [principles-design](../principles-design/SKILL.md) for applicability. Preserve established project conventions; these are defaults for Django/DRF work.

- Map bounded contexts to existing apps; one context may contain several apps. Default layout per app: `models.py`, `services.py`, `selectors.py`, `api/` (views, serializers, urls), `tests/` with `factories.py`.
- Keep substantial use cases/invariants in services or model methods; simple CRUD may use standard DRF views/serializers without pass-through services. Scoped QuerySets may flow to DRF views for filtering/pagination; preserve tenant boundaries.
- Permissions are explicit on every view (`permission_classes`), plus object-level checks for tenant or ownership.
- Querysets in selectors use `select_related`/`prefetch_related`; new list endpoints get a query-count test (`django_assert_num_queries`).
- Preserve the existing background-job system. Use Celery when already selected or justified; make eligible retries bounded and safe, with backoff. Do not introduce a broker for ordinary CRUD.
- Tests: prefer real database behavior for ORM/integration tests; isolate external services as appropriate. Reuse project tools (pytest-django, factory_boy and `APIClient` are defaults). Migrations generated, never hand-edited after merge.
- Settings via environment (django-environ or pydantic-settings); `DEBUG=False`, secure cookies and HSTS outside dev.
- Use the project's schema generator for API changes. drf-spectacular is the default when selecting a new DRF generator; use the project command and path.
- Quality: `ruff check`, `ruff format`, `mypy` (django-stubs), `bandit -r`, `pytest`, `python manage.py makemigrations --check`.
