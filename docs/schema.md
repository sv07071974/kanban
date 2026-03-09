# SQLite schema proposal

## Overview

This schema supports a single board per user for the MVP but keeps the model ready for multiple boards later. It keeps ordering with explicit integer positions and uses text IDs to allow client-generated IDs.

## Tables

### users
- `id` (text, primary key)
- `username` (text, unique, required)
- `created_at` (text, required)

### boards
- `id` (text, primary key)
- `user_id` (text, required, references users.id)
- `title` (text, required)
- `created_at` (text, required)

### columns
- `id` (text, primary key)
- `board_id` (text, required, references boards.id)
- `title` (text, required)
- `position` (integer, required)

### cards
- `id` (text, primary key)
- `column_id` (text, required, references columns.id)
- `title` (text, required)
- `details` (text, required)
- `position` (integer, required)
- `created_at` (text, required)

## Relationships

- One user has many boards.
- One board has many columns.
- One column has many cards.

## Ordering strategy

- Columns are ordered by `position` within a board.
- Cards are ordered by `position` within a column.
- Reordering updates affected positions in a transaction.

## Rationale

- Text IDs support simple client-generated IDs for optimistic UI.
- Explicit position fields avoid fragile ordering by timestamp.
- Separate columns table allows renaming and reordering without touching cards.
- `created_at` is stored as ISO-8601 text for readability and portability.

## Indexes

- users.username (unique)
- boards.user_id
- columns.board_id, columns.position
- cards.column_id, cards.position
