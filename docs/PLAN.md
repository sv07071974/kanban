# High level steps for project

Status (Mar 9, 2026)
- Parts 1-10 completed.
- AI e2e test requires OPENROUTER_API_KEY in environment.

Part 1: Plan

Checklist
- Enrich this document with detailed steps, tests, and success criteria for each part.
- Review existing frontend/AGENTS.md and update it if needed for accuracy and completeness.
- Confirm Docker redo scope and assumptions (single container, uv, FastAPI serves Next build).
- Ensure the user reviews and approves the updated plan before implementation starts.

Tests
- None (planning only).

Success criteria
- Plan includes clear, testable checklists per part.
- User approval is explicitly recorded before any implementation work.

Part 2: Scaffolding

Checklist
- Redo Docker setup for a single-container build.
- Use multi-stage builds to produce a clean runtime image.
- Install Python deps with uv in the image build.
- Build the NextJS frontend inside the image.
- Serve backend and static frontend from one process.
- Ensure runtime config is driven by environment (.env for local, runtime env for container).
- Initialize backend FastAPI app with a minimal health endpoint.
- Serve a static HTML "hello world" at / to validate static serving.
- Add scripts/ start and stop scripts for macOS, Linux, and Windows.
- Add a top-level README note on how to start and stop locally.

Tests
- Backend unit test for health endpoint.
- Container build/run smoke check via scripts.

Success criteria
- `start` script brings up a container that serves / and /api/health.
- `stop` script cleanly stops the container.
- Docker build completes without warnings or manual steps.

Part 3: Add in Frontend

Checklist
- Integrate the existing frontend build output into the container image.
- Serve the static Next build at / via FastAPI static serving.
- Keep any demo data behavior unchanged.
- Confirm the frontend build uses correct public base path.
- Add unit tests for core Kanban logic if missing.
- Add integration tests for loading the Kanban UI.

Tests
- Vitest unit tests for Kanban state helpers.
- Playwright UI flow: load / and see columns and cards.

Success criteria
- / renders the demo Kanban board in the container.
- Tests pass locally and in container.

Part 4: Add in a fake user sign in experience

Checklist
- Add a login UI gate at / for unauthenticated users.
- Accept only "user" / "password".
- Persist login state for the session.
- Add a logout control to return to login screen.
- Keep UI state isolated from future real auth implementation.

Tests
- Playwright UI flow: login, see Kanban, logout, see login.
- Backend unit test for auth stub if applicable.

Success criteria
- Unauthenticated users see login screen.
- Authenticated users see the Kanban and can log out.

Part 5: Database modeling

Checklist
- Propose a SQLite schema for users, boards, columns, and cards.
- Include primary keys, foreign keys, and ordering fields.
- Specify indexing and uniqueness needs.
- Save schema as JSON in docs/.
- Document schema rationale and relationships in docs/.
- Obtain explicit user approval.

Tests
- None (design only).

Success criteria
- Schema is documented, reviewed, and approved.

Part 6: Backend

Checklist
- Implement DB initialization with automatic creation.
- Add API routes to load a user Kanban.
- Add API routes to create, edit, move, and delete cards.
- Add API routes to rename columns and reorder columns.
- Ensure API returns consistent JSON shapes.
- Add backend unit tests for CRUD and validation.
- Confirm error handling for invalid IDs and malformed input.

Tests
- FastAPI tests for get/update Kanban.
- DB initialization test creates tables on empty db.
- Validation tests for required fields and ID existence.

Success criteria
- API supports reading and updating a Kanban for a user.
- All backend tests pass.

Part 7: Frontend + Backend

Checklist
- Replace demo data with API-backed data loading.
- Wire create/edit/move card actions to API.
- Wire column rename actions to API.
- Ensure optimistic updates or reload on success.
- Handle loading and error states consistently.
- Add integration tests for UI + API flow.

Tests
- Playwright UI flow: create, edit, move card persists on reload.
- Playwright UI flow: rename column persists on reload.
- Backend tests remain green.

Success criteria
- Kanban state persists across reloads.
- UI and API behaviors are consistent.

Part 8: AI connectivity

Checklist
- Add OpenRouter client in backend.
- Load OPENROUTER_API_KEY from environment.
- Use model `openai/gpt-oss-120b` for requests.
- Implement a simple test route or service for "2+2".
- Provide a minimal request/response logging strategy.

Tests
- Backend unit/integration test mocks OpenRouter call.
- Manual smoke test if needed.

Success criteria
- Verified ability to call OpenRouter using configured model.

Part 9: AI structured outputs

Checklist
- Define a structured output schema for AI responses (AI decides schema; document it).
- Send Kanban JSON, user question, and conversation history to model.
- Validate and apply optional Kanban updates.
- Keep schema validation strict and deterministic.
- Add tests for schema parsing and update application.

Tests
- Backend tests for schema validation and update application.
- Mocked AI responses covering no-op and update cases.

Success criteria
- AI responses parse deterministically and safely update Kanban when requested.

Part 10: AI chat UI

Checklist
- Build sidebar chat UI with message history.
- Send user messages to backend AI endpoint.
- Render AI response and refresh Kanban on updates.
- Handle loading and error UI for chat requests.
- Add UI tests for chat flow and Kanban update.

Tests
- Playwright UI flow: ask AI to add card, see card appear.
- UI unit tests for chat components where appropriate.

Success criteria
- Chat UI works end to end and Kanban updates when AI requests changes.