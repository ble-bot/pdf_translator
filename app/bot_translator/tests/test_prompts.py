from app.langchain.prompts import build_translation_prompt


class TestPrompts:
    def test_build_translation_prompt(self):
        prompt = build_translation_prompt()
        assert prompt is not None

        messages = prompt.messages
        assert len(messages) == 2
        assert "system" in messages[0].pretty_repr().lower() or "system" in str(type(messages[0])).lower()
