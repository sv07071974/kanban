import httpx

from app.openrouter import call_openrouter


def test_call_openrouter_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://openrouter.ai/api/v1/chat/completions")
        assert request.headers.get("Authorization") == "Bearer test-key"
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "4",
                        }
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    response = call_openrouter(
        [{"role": "user", "content": "2+2"}],
        "test-key",
        client=client,
    )
    assert response == "4"
