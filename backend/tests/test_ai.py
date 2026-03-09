import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.ai import (
    AiResponse,
    CreateCardUpdate,
    RenameColumnUpdate,
    apply_ai_updates,
    parse_ai_response,
)
from app.db import init_db
from app.main import create_app


def test_parse_ai_response_valid() -> None:
    payload = {
        "reply": "Done.",
        "updates": [
            {"type": "rename_column", "column_id": "col-backlog", "title": "Next"}
        ],
    }
    parsed = parse_ai_response(json.dumps(payload))
    assert isinstance(parsed, AiResponse)
    assert parsed.reply == "Done."
    assert parsed.updates[0].type == "rename_column"


def test_parse_ai_response_invalid() -> None:
    try:
        parse_ai_response("not-json")
    except ValueError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("Expected parse failure")


def test_apply_ai_updates(tmp_path: Path) -> None:
    db_path = str(tmp_path / "test.db")
    app = create_app(db_path)
    client = TestClient(app)
    init_db(db_path)
    client.get("/api/kanban")

    response = apply_ai_updates(
        db_path,
        [
            RenameColumnUpdate(
                type="rename_column",
                column_id="col-backlog",
                title="Next",
            ),
            CreateCardUpdate(
                type="create_card",
                column_id="col-backlog",
                title="AI card",
                details="Notes",
            ),
        ],
    )
    column = next(col for col in response["columns"] if col["id"] == "col-backlog")
    assert column["title"] == "Next"
    assert any(
        card["title"] == "AI card" for card in response["cards"].values()
    )
