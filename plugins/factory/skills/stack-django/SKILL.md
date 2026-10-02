---
name: stack-django
description: How we build Django/DRF backends - app layout, thin views, services and selectors, permissions, Celery, tests, settings and quality commands. Use when writing or reviewing Python backend code.
---
- Layout per app: `models.py`, `services.py`, `selectors.py`, `api/` (views, serializers, urls), `tests/` with `factories.py`.
- Views are thin: parse → call service/selector → serialize. Serializers validate shape, services validate rules.
- Permissions are explicit on every view (`permission_classes`), plus object-level checks for tenant or ownership.
- Querysets in selectors use `select_related`/`prefetch_related`; new list endpoints get a query-count test (`django_assert_num_queries`).
- Background work in Celery tasks that call services; tasks are idempotent and retry with backoff.
- Tests: pytest-django, factory_boy, `APIClient`; no DB mocking. Migrations generated, never hand-edited after merge.
- Settings via environment (django-environ or pydantic-settings); `DEBUG=False`, secure cookies and HSTS outside dev.
- OpenAPI schema with drf-spectacular: `python manage.py spectacular --file schema.yml` after any API change.
- Quality: `ruff check`, `ruff format`, `mypy` (django-stubs), `bandit -r`, `pytest`, `python manage.py makemigrations --check`.
