from __future__ import annotations

import re


class RecursiveCharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        separators: list[str] | None = None,
        length_function: callable = len,
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._separators = separators or ["\n\n\n", "\n\n", "\n", ".", " ", ""]
        self._length_function = length_function

    def split_text(self, text: str) -> list[str]:
        return self._split_text(text, self._separators)

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        final_chunks: list[str] = []

        # Find the first separator that exists in the text
        separator = separators[-1]
        new_separators: list[str] = []
        for i, s in enumerate(separators):
            if s == "":
                separator = s
                break
            if s in text:
                separator = s
                new_separators = separators[i + 1:]
                break

        # Split by separator
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)

        good_splits: list[str] = []
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                
                if not new_separators:
                    final_chunks.append(s)
                else:
                    final_chunks.extend(self._split_text(s, new_separators))

        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)

        return final_chunks

    def _merge_splits(self, splits: list[str], separator: str) -> list[str]:
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for s in splits:
            s_len = self._length_function(s)
            sep_len = self._length_function(separator) if current_chunk else 0
            
            if current_length + s_len + sep_len <= self._chunk_size:
                current_chunk.append(s)
                current_length += s_len + sep_len
            else:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                current_chunk = [s]
                current_length = s_len

        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return chunks


def build_text_splitter(
    chunk_size: int = 2000,
    chunk_overlap: int = 200,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
