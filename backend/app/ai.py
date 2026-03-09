from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.db import (
    create_card,
    delete_card,
    get_board_data,
    move_card,
    rename_column,
    update_card,
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class RenameColumnUpdate(BaseModel):
    type: Literal["rename_column"]
    column_id: str
    title: str


class CreateCardUpdate(BaseModel):
    type: Literal["create_card"]
    column_id: str
    title: str
    details: str | None = None


class UpdateCardUpdate(BaseModel):
    type: Literal["update_card"]
    card_id: str
    title: str | None = None
    details: str | None = None

    @model_validator(mode="after")
    def ensure_updates(self) -> "UpdateCardUpdate":
        if self.title is None and self.details is None:
            raise ValueError("update_card requires title or details")
        return self


class MoveCardUpdate(BaseModel):
    type: Literal["move_card"]
    card_id: str
    to_column_id: str
    position: int | None = None


class DeleteCardUpdate(BaseModel):
    type: Literal["delete_card"]
    card_id: str


UpdateAction = (
    RenameColumnUpdate
    | CreateCardUpdate
    | UpdateCardUpdate
    | MoveCardUpdate
    | DeleteCardUpdate
)


class AiResponse(BaseModel):
    reply: str
    updates: list[UpdateAction] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


def build_ai_messages(board: dict, history: list[ChatMessage], message: str) -> list[dict[str, str]]:
    schema = {
        "reply": "string",
        "updates": [
            {
                "type": "rename_column",
                "column_id": "col-backlog",
                "title": "New name",
            },
            {
                "type": "create_card",
                "column_id": "col-backlog",
                "title": "Title",
                "details": "Details",
            },
            {
                "type": "update_card",
                "card_id": "card-1",
                "title": "New title",
                "details": "New details",
            },
            {
                "type": "move_card",
                "card_id": "card-1",
                "to_column_id": "col-review",
                "position": 0,
            },
            {
                "type": "delete_card",
                "card_id": "card-1",
            },
        ],
    }

    system_content = (
        "You are a Kanban assistant. "
        "Return a single JSON object only, no markdown. "
        "Use this schema and omit fields not needed."
    )
    board_payload = json.dumps(board)
    schema_payload = json.dumps(schema)

    messages: list[dict[str, str]] = [{"role": "system", "content": system_content}]
    messages.extend({"role": entry.role, "content": entry.content} for entry in history)
    messages.append(
        {
            "role": "user",
            "content": (
                "Current board JSON: "
                f"{board_payload}\n"
                "Schema example: "
                f"{schema_payload}\n"
                "User request: "
                f"{message}"
            ),
        }
    )

    return messages


def parse_ai_response(content: str) -> AiResponse:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("AI response is not valid JSON") from exc

    try:
        return AiResponse.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("AI response schema invalid") from exc


def apply_ai_updates(db_path: str, updates: list[UpdateAction]) -> dict:
    if not updates:
        return get_board_data(db_path)

    board: dict | None = None
    for update in updates:
        if isinstance(update, RenameColumnUpdate):
            board = rename_column(db_path, update.column_id, update.title)
        elif isinstance(update, CreateCardUpdate):
            board = create_card(
                db_path,
                update.column_id,
                update.title,
                update.details or "",
            )
        elif isinstance(update, UpdateCardUpdate):
            board = update_card(db_path, update.card_id, update.title, update.details)
        elif isinstance(update, MoveCardUpdate):
            board = move_card(
                db_path,
                update.card_id,
                update.to_column_id,
                update.position,
            )
        elif isinstance(update, DeleteCardUpdate):
            board = delete_card(db_path, update.card_id)

    return board if board is not None else get_board_data(db_path)
