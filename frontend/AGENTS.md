# Frontend agent notes

## Overview

This is a NextJS app (app router) that renders a single Kanban board UI backed
by the FastAPI API. State loads from the backend, and updates persist via API
calls. Drag and drop uses dnd-kit. Styling is Tailwind v4 with CSS variables in
globals. A chat sidebar calls the AI endpoint and applies updates.

## Key entry points

- App entry: src/app/page.tsx renders the Kanban board.
- Layout: src/app/layout.tsx sets global fonts and metadata.
- Styles: src/app/globals.css defines the design tokens used across the UI.

## Core modules

- src/components/KanbanBoard.tsx: loads board state from API, handles drag and drop, and renders columns.
- src/components/KanbanColumn.tsx: renders a single column, supports rename, add card, and drop target behavior.
- src/components/KanbanCard.tsx: renders a draggable card with delete.
- src/components/KanbanCardPreview.tsx: drag overlay preview.
- src/components/NewCardForm.tsx: add-card form and inline toggle.
- src/components/ChatSidebar.tsx: chat UI that calls AI endpoint and refreshes board.
- src/lib/kanban.ts: board data model and card move logic.
- src/lib/api.ts: API client for Kanban and AI chat.

## State and behavior

- Board state loads from `/api/kanban` and updates persist via API calls.
- Column rename commits on blur/enter.
- Card create, move, and delete call the backend and refresh board state.
- Chat sidebar sends prompts to `/api/ai/chat` and applies updates.
- Drag and drop uses DndContext with PointerSensor and closestCorners collision.

## Tests

- Unit tests: src/components/KanbanBoard.test.tsx and src/lib/kanban.test.ts (Vitest + Testing Library).
- E2E tests: tests/kanban.spec.ts (Playwright). AI test is optional and requires OPENROUTER_API_KEY.
- Test scripts: see package.json (test:unit, test:e2e, test:all).

## Dev scripts

- npm run dev (Next dev server)
- npm run build (Next build)
- npm run test:unit (Vitest)
- npm run test:e2e (Playwright)
