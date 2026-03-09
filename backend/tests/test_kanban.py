from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "test.db"
    app = create_app(str(db_path))
    return TestClient(app)


def test_get_kanban_seeded(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/api/kanban")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload["columns"]) == 5
        assert len(payload["cards"]) == 8


def test_rename_column(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.patch(
            "/api/columns/col-backlog", json={"title": "New Name"}
        )
        assert response.status_code == 200
        payload = response.json()
        column = next(col for col in payload["columns"] if col["id"] == "col-backlog")
        assert column["title"] == "New Name"


def test_create_move_delete_card(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/api/cards",
            json={
                "column_id": "col-backlog",
                "title": "New card",
                "details": "Details",
            },
        )
        assert response.status_code == 200
        payload = response.json()
        card_id = next(
            card_id
            for card_id, card in payload["cards"].items()
            if card["title"] == "New card"
        )

        response = client.post(
            f"/api/cards/{card_id}/move",
            json={"to_column_id": "col-review", "position": 0},
        )
        assert response.status_code == 200
        payload = response.json()
        review_column = next(col for col in payload["columns"] if col["id"] == "col-review")
        assert payload["cards"][card_id]["title"] == "New card"
        assert review_column["cardIds"][0] == card_id

        response = client.delete(f"/api/cards/{card_id}")
        assert response.status_code == 200
        payload = response.json()
        assert card_id not in payload["cards"]


def test_reorder_columns(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/api/kanban")
        assert response.status_code == 200
        columns = response.json()["columns"]
        column_ids = [column["id"] for column in columns][::-1]

        response = client.post("/api/columns/reorder", json={"column_ids": column_ids})
        assert response.status_code == 200
        updated = response.json()["columns"]
        assert [column["id"] for column in updated] == column_ids
