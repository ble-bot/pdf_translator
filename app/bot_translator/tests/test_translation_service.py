import pytest
from app.langchain.splitter import build_text_splitter


class TestTextSplitter:
    @pytest.fixture
    def splitter(self):
        return build_text_splitter(chunk_size=100, chunk_overlap=20)

    def test_split_small_text(self, splitter):
        text = "Hello world."
        chunks = splitter.split_text(text)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world."

    def test_split_large_text(self, splitter):
        text = " ".join(["word"] * 50)
        chunks = splitter.split_text(text)
        assert len(chunks) >= 1

    def test_split_preserves_words(self, splitter):
        text = " ".join([f"word{i}" for i in range(30)])
        chunks = splitter.split_text(text)
        reconstructed = " ".join(chunks)
        for w in [f"word{i}" for i in range(30)]:
            assert w in reconstructed
