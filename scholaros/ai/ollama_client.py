"""
ScholarOS
Ollama Client

Version : 1.0
Status  : Frozen
Python  : 3.14+

Description
-----------
Low-level HTTP client for communicating with a
local Ollama server.

Responsibilities
----------------
• Send prompts to Ollama
• Receive model responses
• Return AIResponse objects

The client performs no prompt engineering,
template rendering, or business logic.
"""

from __future__ import annotations

from typing import Any

import httpx

from scholaros.ai.response import AIResponse


class OllamaClient:
    """
    Low-level client for the Ollama REST API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
    ) -> None:

        self._base_url = base_url.rstrip("/")

        self._client = httpx.Client(
            timeout=120.0,
        )

    def generate(
        self,
        *,
        model: str,
        prompt: str,
    ) -> AIResponse:
        """
        Generate a response from an Ollama model.
        """

        payload = self._build_payload(
            model=model,
            prompt=prompt,
        )

        response = self._post(payload)

        return self._parse_response(response)

    def _build_payload(
        self,
        *,
        model: str,
        prompt: str,
    ) -> dict[str, Any]:
        """
        Build the request payload for the Ollama API.
        """

        return {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

    def _post(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send a request to the Ollama generate endpoint.
        """

        response = self._client.post(
            f"{self._base_url}/api/generate",
            json=payload,
        )

        response.raise_for_status()

        return response.json()

    def _parse_response(
        self,
        response: dict[str, Any],
    ) -> AIResponse:
        """
        Convert an Ollama response into an AIResponse.
        """

        return AIResponse(
            content=response.get(
                "response",
                "",
            ),
            model=response.get(
                "model",
                "",
            ),
            prompt_tokens=response.get(
                "prompt_eval_count",
                0,
            ),
            completion_tokens=response.get(
                "eval_count",
                0,
            ),
            total_tokens=(
                response.get(
                    "prompt_eval_count",
                    0,
                )
                + response.get(
                    "eval_count",
                    0,
                )
            ),
        )

    def close(self) -> None:
        """
        Close the underlying HTTP client.
        """

        self._client.close()
    def __enter__(self) -> "OllamaClient":
        """
        Enter the client context.
        """

        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """
        Exit the client context.
        """

        self.close()