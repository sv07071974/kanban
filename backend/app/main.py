from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.ai import ChatRequest, apply_ai_updates, build_ai_messages, parse_ai_response
from app.db import (
    create_card,
    delete_card,
    get_board_data,
    get_default_db_path,
    init_db,
    move_card,
    rename_column,
    reorder_columns,
    update_card,
)
from app.openrouter import call_openrouter, get_openrouter_key


class ColumnRenameRequest(BaseModel):
    title: str


class ColumnReorderRequest(BaseModel):
    column_ids: list[str]


class CardCreateRequest(BaseModel):
    column_id: str
    title: str
    details: str | None = None


class CardUpdateRequest(BaseModel):
    title: str | None = None
    details: str | None = None


class CardMoveRequest(BaseModel):
    to_column_id: str
    position: int | None = None


def create_app(db_path: str | None = None) -> FastAPI:
    app = FastAPI()
    resolved_db_path = db_path or get_default_db_path()

    @app.on_event("startup")
    def startup() -> None:
        init_db(resolved_db_path)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/ai/test")
    def ai_test() -> dict:
        try:
            api_key = get_openrouter_key()
            answer = call_openrouter(
                [{"role": "user", "content": "2+2"}],
                api_key,
            )
            return {"answer": answer}
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - network error surface
            raise HTTPException(status_code=502, detail="OpenRouter call failed") from exc

    @app.post("/api/ai/chat")
    def ai_chat(payload: ChatRequest) -> dict:
        try:
            api_key = get_openrouter_key()
            board = get_board_data(resolved_db_path)
            messages = build_ai_messages(board, payload.history, payload.message)
            raw_response = call_openrouter(messages, api_key)
            ai_response = parse_ai_response(raw_response)
            updated_board = apply_ai_updates(resolved_db_path, ai_response.updates)
            return {"reply": ai_response.reply, "board": updated_board}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - network error surface
            raise HTTPException(status_code=502, detail="OpenRouter call failed") from exc

    @app.get("/api/kanban")
    def get_kanban() -> dict:
        try:
            return get_board_data(resolved_db_path)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.patch("/api/columns/{column_id}")
    def patch_column(column_id: str, payload: ColumnRenameRequest) -> dict:
        try:
            return rename_column(resolved_db_path, column_id, payload.title)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/columns/reorder")
    def post_columns_reorder(payload: ColumnReorderRequest) -> dict:
        try:
            return reorder_columns(resolved_db_path, payload.column_ids)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/cards")
    def post_card(payload: CardCreateRequest) -> dict:
        try:
            return create_card(
                resolved_db_path,
                payload.column_id,
                payload.title,
                payload.details or "",
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.patch("/api/cards/{card_id}")
    def patch_card(card_id: str, payload: CardUpdateRequest) -> dict:
        try:
            return update_card(resolved_db_path, card_id, payload.title, payload.details)
        except ValueError as exc:
            status = 400 if str(exc) == "No fields to update" else 404
            raise HTTPException(status_code=status, detail=str(exc)) from exc

    @app.post("/api/cards/{card_id}/move")
    def post_card_move(card_id: str, payload: CardMoveRequest) -> dict:
        try:
            return move_card(
                resolved_db_path, card_id, payload.to_column_id, payload.position
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.delete("/api/cards/{card_id}")
    def delete_card_route(card_id: str) -> dict:
        try:
            return delete_card(resolved_db_path, card_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


app = create_app()
