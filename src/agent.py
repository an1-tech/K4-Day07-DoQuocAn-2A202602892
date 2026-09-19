from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)

        if results:
            context_parts = []

            for index, result in enumerate(results, start=1):
                source_id = result["metadata"].get("doc_id", result["id"])
                context_parts.append(
                    f"[Nguồn {index}: {source_id}]\n{result['content']}"
                )

            context = "\n\n".join(context_parts)
        else:
            context = "Không tìm thấy tài liệu liên quan trong knowledge base."

        prompt = f"""Bạn là trợ lý trả lời dựa trên tài liệu được cung cấp.
Chỉ sử dụng thông tin trong Context. Nếu Context không đủ, hãy nói rõ.

Context:
{context}

Question:
{question}

Answer:
"""

        return self.llm_fn(prompt)