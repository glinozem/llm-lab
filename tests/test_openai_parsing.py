from __future__ import annotations

import httpx

from llm_lab.clients.openai_client import OpenAIClient


def test_openai_generate_parses_output_text() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/responses"
        return httpx.Response(
            200,
            json={
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "hello"}],
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    c = OpenAIClient(api_key="k", model="m", base_url="https://api.openai.com", _http=http)
    assert c.generate([{"role": "user", "content": "hi"}]) == "hello"
