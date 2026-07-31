from scholaros.ai.llm import (
    Message,
    MessageRole,
    OllamaLLM,
)


def test_ollama_generate():

    llm = OllamaLLM()

    response = llm.generate(
        [
            Message(
                role=MessageRole.USER,
                content="Reply with exactly one word: ScholarOS",
            )
        ]
    )

    assert response.content
    assert isinstance(response.content, str)

    