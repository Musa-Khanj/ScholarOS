from __future__ import annotations

import re

from scholaros.ai.llm.message import (
    Message,
    MessageRole,
)
from scholaros.ai.prompt.prompt import Prompt


class PromptRenderer:
    """
    Renders prompt templates into immutable Prompt objects.
    """

    _VARIABLE_PATTERN = re.compile(
        r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"
    )

    def render(
        self,
        template: str,
        *,
        role: MessageRole = MessageRole.USER,
        **variables: object,
    ) -> Prompt:

        content = template

        required = set(
            self._VARIABLE_PATTERN.findall(template)
        )

        missing = required - variables.keys()

        if missing:

            missing_names = ", ".join(
                sorted(missing)
            )

            raise ValueError(
                f"Missing template variables: {missing_names}"
            )

        for name in required:

            value = str(
                variables[name]
            )

            content = re.sub(
                rf"\{{\{{\s*{name}\s*\}}\}}",
                value,
                content,
            )

        return Prompt(
            messages=[
                Message(
                    role=role,
                    content=content,
                )
            ]
        )