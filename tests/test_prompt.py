from scholaros.ai.llm import Message, MessageRole
from scholaros.ai.prompt import Prompt


def test_prompt_creation():

    prompt = Prompt(
        messages=[
            Message(
                role=MessageRole.USER,
                content="Hello",
            )
        ]
    )

    assert len(prompt.messages) == 1
    assert prompt.messages[0].content == "Hello"