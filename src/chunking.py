from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = max(1, chunk_size)
        self.overlap = max(0, min(overlap, self.chunk_size - 1))

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []

        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)

            if start + self.chunk_size >= len(text):
                break

        return chunks


class SentenceChunker:
    """
    Split text into chunks containing at most max_sentences_per_chunk sentences.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Tách sau dấu . ! ? và khoảng trắng hoặc xuống dòng phía sau.
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

        chunks: list[str] = []

        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[start : start + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))

        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
    ) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = max(1, chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        return self._split(text.strip(), self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        current_text = current_text.strip()

        if not current_text:
            return []

        if len(current_text) <= self.chunk_size:
            return [current_text]

        # Không còn separator hoặc separator cuối là "" -> cắt cứng.
        if not remaining_separators or remaining_separators[0] == "":
            return [
                current_text[index : index + self.chunk_size].strip()
                for index in range(0, len(current_text), self.chunk_size)
                if current_text[index : index + self.chunk_size].strip()
            ]

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]

        # Separator hiện tại không xuất hiện thì thử separator ưu tiên kế tiếp.
        if separator not in current_text:
            return self._split(current_text, next_separators)

        parts = [part.strip() for part in current_text.split(separator) if part.strip()]
        chunks: list[str] = []
        buffer = ""

        for part in parts:
            candidate = f"{buffer}{separator}{part}" if buffer else part

            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            # Buffer trước đó đã đủ nhỏ, lưu lại.
            if buffer:
                chunks.append(buffer.strip())

            # Nếu một phần vẫn quá dài, tách tiếp bằng separator sau.
            if len(part) > self.chunk_size:
                chunks.extend(self._split(part, next_separators))
                buffer = ""
            else:
                buffer = part

        if buffer:
            chunks.append(buffer.strip())

        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    norm_a = math.sqrt(sum(value * value for value in vec_a))
    norm_b = math.sqrt(sum(value * value for value in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    @staticmethod
    def _stats(chunks: list[str]) -> dict:
        count = len(chunks)
        avg_length = sum(len(chunk) for chunk in chunks) / count if count else 0.0

        return {
            "chunks": chunks,
            "count": count,
            "avg_length": avg_length,
        }

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed_chunks = FixedSizeChunker(
            chunk_size=chunk_size,
            overlap=min(20, max(0, chunk_size // 10)),
        ).chunk(text)

        sentence_chunks = SentenceChunker(
            max_sentences_per_chunk=3,
        ).chunk(text)

        recursive_chunks = RecursiveChunker(
            chunk_size=chunk_size,
        ).chunk(text)

        return {
            "fixed_size": self._stats(fixed_chunks),
            "by_sentences": self._stats(sentence_chunks),
            "recursive": self._stats(recursive_chunks),
        }