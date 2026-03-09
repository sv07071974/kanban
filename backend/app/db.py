from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

DEFAULT_COLUMNS = [
    {"id": "col-backlog", "title": "Backlog"},
    {"id": "col-discovery", "title": "Discovery"},
    {"id": "col-progress", "title": "In Progress"},
    {"id": "col-review", "title": "Review"},
    {"id": "col-done", "title": "Done"},
]

DEFAULT_CARDS = [
    {
        "id": "card-1",
        "column_id": "col-backlog",
        "title": "Align roadmap themes",
        "details": "Draft quarterly themes with impact statements and metrics.",
    },
    {
        "id": "card-2",
        "column_id": "col-backlog",
        "title": "Gather customer signals",
        "details": "Review support tags, sales notes, and churn feedback.",
    },
    {
        "id": "card-3",
        "column_id": "col-discovery",
        "title": "Prototype analytics view",
        "details": "Sketch initial dashboard layout and key drill-downs.",
    },
    {
        "id": "card-4",
        "column_id": "col-progress",
        "title": "Refine status language",
        "details": "Standardize column labels and tone across the board.",
    },
    {
        "id": "card-5",
        "column_id": "col-progress",
        "title": "Design card layout",
        "details": "Add hierarchy and spacing for scanning dense lists.",
    },
    {
        "id": "card-6",
        "column_id": "col-review",
        "title": "QA micro-interactions",
        "details": "Verify hover, focus, and loading states.",
    },
    {
        "id": "card-7",
        "column_id": "col-done",
        "title": "Ship marketing page",
        "details": "Final copy approved and asset pack delivered.",
    },
    {
        "id": "card-8",
        "column_id": "col-done",
        "title": "Close onboarding sprint",
        "details": "Document release notes and share internally.",
    },
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS boards (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS columns (
  id TEXT PRIMARY KEY,
  board_id TEXT NOT NULL,
  title TEXT NOT NULL,
  position INTEGER NOT NULL,
  FOREIGN KEY (board_id) REFERENCES boards(id)
);

CREATE TABLE IF NOT EXISTS cards (
  id TEXT PRIMARY KEY,
  column_id TEXT NOT NULL,
  title TEXT NOT NULL,
  details TEXT NOT NULL,
  position INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE
);
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_default_db_path() -> str:
    env_path = os.getenv("PM_DB_PATH")
    if env_path:
        return env_path
    return str(Path(__file__).resolve().parent / "pm.db")


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        user_id = _get_or_create_user(conn, "user")
        board_id = _get_or_create_board(conn, user_id, "Kanban Board")
        _seed_board_if_empty(conn, board_id)


def _get_or_create_user(conn: sqlite3.Connection, username: str) -> str:
    row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        return row["id"]
    user_id = f"user-{uuid4().hex}"
    conn.execute(
        "INSERT INTO users (id, username, created_at) VALUES (?, ?, ?)",
        (user_id, username, _utc_now()),
    )
    return user_id


def _get_or_create_board(
    conn: sqlite3.Connection, user_id: str, title: str
) -> str:
    row = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user_id,)).fetchone()
    if row:
        return row["id"]
    board_id = f"board-{uuid4().hex}"
    conn.execute(
        "INSERT INTO boards (id, user_id, title, created_at) VALUES (?, ?, ?, ?)",
        (board_id, user_id, title, _utc_now()),
    )
    return board_id


def _seed_board_if_empty(conn: sqlite3.Connection, board_id: str) -> None:
    row = conn.execute(
        "SELECT COUNT(1) AS count FROM columns WHERE board_id = ?", (board_id,)
    ).fetchone()
    if row and row["count"] > 0:
        return

    conn.executemany(
        "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
        [
            (column["id"], board_id, column["title"], index)
            for index, column in enumerate(DEFAULT_COLUMNS)
        ],
    )

    cards_by_column = {column["id"]: [] for column in DEFAULT_COLUMNS}
    for card in DEFAULT_CARDS:
        cards_by_column[card["column_id"]].append(card)

    for column_id, cards in cards_by_column.items():
        conn.executemany(
            "INSERT INTO cards (id, column_id, title, details, position, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    card["id"],
                    column_id,
                    card["title"],
                    card["details"],
                    index,
                    _utc_now(),
                )
                for index, card in enumerate(cards)
            ],
        )


def get_board_data(db_path: str, username: str = "user") -> dict:
    with get_connection(db_path) as conn:
        user_row = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not user_row:
            raise ValueError("User not found")
        board_row = conn.execute(
            "SELECT id FROM boards WHERE user_id = ?", (user_row["id"],)
        ).fetchone()
        if not board_row:
            raise ValueError("Board not found")
        return _load_board(conn, board_row["id"])


def _load_board(conn: sqlite3.Connection, board_id: str) -> dict:
    column_rows = conn.execute(
        "SELECT id, title, position FROM columns WHERE board_id = ? ORDER BY position",
        (board_id,),
    ).fetchall()

    columns = [
        {"id": row["id"], "title": row["title"], "cardIds": []}
        for row in column_rows
    ]

    if not columns:
        return {"columns": [], "cards": {}}

    column_ids = [column["id"] for column in columns]
    placeholders = ",".join("?" for _ in column_ids)
    card_rows = conn.execute(
        f"SELECT id, column_id, title, details, position FROM cards"
        f" WHERE column_id IN ({placeholders}) ORDER BY position",
        column_ids,
    ).fetchall()

    cards = {}
    cards_by_column: dict[str, list[str]] = {column_id: [] for column_id in column_ids}
    for row in card_rows:
        cards[row["id"]] = {
            "id": row["id"],
            "title": row["title"],
            "details": row["details"],
        }
        cards_by_column[row["column_id"]].append(row["id"])

    for column in columns:
        column["cardIds"] = cards_by_column[column["id"]]

    return {"columns": columns, "cards": cards}


def rename_column(db_path: str, column_id: str, title: str) -> dict:
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, board_id FROM columns WHERE id = ?", (column_id,)
        ).fetchone()
        if not row:
            raise ValueError("Column not found")
        conn.execute("UPDATE columns SET title = ? WHERE id = ?", (title, column_id))
        return _load_board(conn, row["board_id"])


def reorder_columns(db_path: str, column_ids: Iterable[str]) -> dict:
    column_ids = list(column_ids)
    with get_connection(db_path) as conn:
        if not column_ids:
            raise ValueError("Column list is empty")
        board_row = conn.execute(
            "SELECT board_id FROM columns WHERE id = ?", (column_ids[0],)
        ).fetchone()
        if not board_row:
            raise ValueError("Column not found")
        board_id = board_row["board_id"]
        existing_rows = conn.execute(
            "SELECT id FROM columns WHERE board_id = ?", (board_id,)
        ).fetchall()
        existing_ids = {row["id"] for row in existing_rows}
        if set(column_ids) != existing_ids:
            raise ValueError("Column list does not match board")
        conn.executemany(
            "UPDATE columns SET position = ? WHERE id = ?",
            [(index, column_id) for index, column_id in enumerate(column_ids)],
        )
        return _load_board(conn, board_id)


def create_card(db_path: str, column_id: str, title: str, details: str) -> dict:
    details = details or "No details yet."
    with get_connection(db_path) as conn:
        column_row = conn.execute(
            "SELECT id, board_id FROM columns WHERE id = ?", (column_id,)
        ).fetchone()
        if not column_row:
            raise ValueError("Column not found")
        count_row = conn.execute(
            "SELECT COUNT(1) AS count FROM cards WHERE column_id = ?",
            (column_id,),
        ).fetchone()
        position = count_row["count"] if count_row else 0
        card_id = f"card-{uuid4().hex}"
        conn.execute(
            "INSERT INTO cards (id, column_id, title, details, position, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (card_id, column_id, title, details, position, _utc_now()),
        )
        return _load_board(conn, column_row["board_id"])


def update_card(db_path: str, card_id: str, title: str | None, details: str | None) -> dict:
    with get_connection(db_path) as conn:
        card_row = conn.execute(
            "SELECT id, column_id FROM cards WHERE id = ?", (card_id,)
        ).fetchone()
        if not card_row:
            raise ValueError("Card not found")
        updates = []
        params: list[object] = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if details is not None:
            updates.append("details = ?")
            params.append(details)
        if not updates:
            raise ValueError("No fields to update")
        params.append(card_id)
        conn.execute(f"UPDATE cards SET {', '.join(updates)} WHERE id = ?", params)
        board_id = _get_board_id_for_column(conn, card_row["column_id"])
        return _load_board(conn, board_id)


def delete_card(db_path: str, card_id: str) -> dict:
    with get_connection(db_path) as conn:
        card_row = conn.execute(
            "SELECT id, column_id FROM cards WHERE id = ?", (card_id,)
        ).fetchone()
        if not card_row:
            raise ValueError("Card not found")
        column_id = card_row["column_id"]
        board_id = _get_board_id_for_column(conn, column_id)
        conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        _resequence_cards(conn, column_id)
        return _load_board(conn, board_id)


def move_card(
    db_path: str, card_id: str, to_column_id: str, position: int | None
) -> dict:
    with get_connection(db_path) as conn:
        card_row = conn.execute(
            "SELECT id, column_id FROM cards WHERE id = ?", (card_id,)
        ).fetchone()
        if not card_row:
            raise ValueError("Card not found")
        from_column_id = card_row["column_id"]

        target_row = conn.execute(
            "SELECT id, board_id FROM columns WHERE id = ?", (to_column_id,)
        ).fetchone()
        if not target_row:
            raise ValueError("Column not found")

        if from_column_id == to_column_id:
            card_ids = _get_card_ids(conn, from_column_id)
            if card_id in card_ids:
                card_ids.remove(card_id)
            insert_index = _normalize_position(position, len(card_ids))
            card_ids.insert(insert_index, card_id)
            _apply_card_positions(conn, from_column_id, card_ids)
            return _load_board(conn, target_row["board_id"])

        from_ids = _get_card_ids(conn, from_column_id)
        if card_id in from_ids:
            from_ids.remove(card_id)
        to_ids = _get_card_ids(conn, to_column_id)
        insert_index = _normalize_position(position, len(to_ids))
        to_ids.insert(insert_index, card_id)
        _apply_card_positions(conn, from_column_id, from_ids)
        _apply_card_positions(conn, to_column_id, to_ids)
        conn.execute(
            "UPDATE cards SET column_id = ? WHERE id = ?",
            (to_column_id, card_id),
        )
        return _load_board(conn, target_row["board_id"])


def _normalize_position(position: int | None, length: int) -> int:
    if position is None:
        return length
    return max(0, min(position, length))


def _get_card_ids(conn: sqlite3.Connection, column_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT id FROM cards WHERE column_id = ? ORDER BY position", (column_id,)
    ).fetchall()
    return [row["id"] for row in rows]


def _apply_card_positions(
    conn: sqlite3.Connection, column_id: str, card_ids: Iterable[str]
) -> None:
    conn.executemany(
        "UPDATE cards SET position = ? WHERE id = ?",
        [(index, card_id) for index, card_id in enumerate(card_ids)],
    )
    conn.execute(
        "UPDATE cards SET position = position WHERE column_id = ?",
        (column_id,),
    )


def _resequence_cards(conn: sqlite3.Connection, column_id: str) -> None:
    card_ids = _get_card_ids(conn, column_id)
    _apply_card_positions(conn, column_id, card_ids)


def _get_board_id_for_column(conn: sqlite3.Connection, column_id: str) -> str:
    row = conn.execute(
        "SELECT board_id FROM columns WHERE id = ?", (column_id,)
    ).fetchone()
    if not row:
        raise ValueError("Column not found")
    return row["board_id"]
