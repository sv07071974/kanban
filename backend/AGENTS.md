# Backend agent notes

## Overview

This FastAPI backend serves the static NextJS build and provides a SQLite-backed
Kanban API. It also includes AI endpoints that call OpenRouter for structured
updates and a simple connectivity test.

## Entry points

- app/main.py: FastAPI app with Kanban, AI, and health routes.
- app/db.py: SQLite schema, seed data, and CRUD helpers.
- app/ai.py: AI schema, parsing, and apply-update helpers.
- app/openrouter.py: OpenRouter client.

## Dependencies

- fastapi, uvicorn for the web server.
- httpx for OpenRouter calls.
- pytest for tests.

## Tests

- tests/test_health.py: validates the /api/health response.
- tests/test_kanban.py: CRUD and ordering behaviors.
- tests/test_openrouter.py: OpenRouter parsing with a mock transport.
- tests/test_ai.py: AI schema parsing and update application.