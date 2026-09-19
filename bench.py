from __future__ import annotations

import argparse
import re
from pathlib import Path

from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    LocalEmbedder,
    _mock_embed,
)

CORPUS_DIR = Path("data/vinuni-library")

# =========================
# CHỈ ĐỔI DÒNG NÀY
# Fixed-size Chunking của Đỗ Quốc An
# =========================
CHUNKER = FixedSizeChunker(chunk_size=500, overlap=50)

BENCHMARKS = [
    {
        "id": "Q1",
        "question": (
            "Với giáo trình tại phòng 111, được mượn tối đa bao nhiêu cuốn, "
            "trong bao lâu và được gia hạn thế nào?"
        ),
        "metadata_filter": {"audience": "student"},
        "gold_doc_id": "student-textbook-borrowing",
        "required_terms": ["tối đa 8 cuốn", "90 ngày"],
    },
    {
        "id": "Q2",
        "question": (
            "Chính sách mượn sách tham khảo tại phòng 102 quy định số lượng, "
            "thời hạn và gia hạn như thế nào?"
        ),
        "metadata_filter": None,
        "gold_doc_id": "student-reference-book-borrowing",
        "required_terms": ["tối đa 5 cuốn", "1 đến 30 ngày"],
    },
    {
        "id": "Q3",
        "question": (
            "Phòng học nhóm phục vụ vào thời gian nào và quy trình nhận trả "
            "chìa khóa ra sao?"
        ),
        "metadata_filter": None,
        "gold_doc_id": "group-study-room",
        "required_terms": ["08:00–21:00", "chìa khóa"],
    },
    {
        "id": "Q4",
        "question": (
            "Khi quên mật khẩu tài khoản thư viện, bạn đọc cần thực hiện "
            "các bước nào?"
        ),
        "metadata_filter": None,
        "gold_doc_id": "library-account",
        "required_terms": ["Quên mật khẩu", "mã số thẻ"],
    },
    {
        "id": "Q5",
        "question": (
            "Bạn đọc ngoài HUST có thể đọc toàn văn tài nguyên số không "
            "và cần điều kiện gì?"
        ),
        "metadata_filter": None,
        "gold_doc_id": "digital-resource-faq",
        "required_terms": ["đăng ký thẻ hoặc tài khoản thư viện"],
    },
]


def parse_markdown_file(path: Path) -> tuple[dict, str]:
    """Đọc frontmatter và content từ một file Markdown."""
    text = path.read_text(encoding="utf-8")

    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"{path} không có frontmatter hợp lệ.")

    frontmatter_text = parts[1]
    content = parts[2].strip()

    metadata = {
        key: value.strip().strip('"')
        for key, value in re.findall(
            r"^(\w+):\s*(.+)$",
            frontmatter_text,
            re.MULTILINE,
        )
    }

    if "doc_id" not in metadata:
        metadata["doc_id"] = path.stem

    return metadata, content


def load_chunked_documents() -> list[Document]:
    """Đọc toàn bộ corpus, chia chunk và giữ metadata ở mọi chunk."""
    documents: list[Document] = []

    for path in sorted(CORPUS_DIR.glob("*.md")):
        metadata, content = parse_markdown_file(path)
        source_doc_id = path.stem

        chunks = CHUNKER.chunk(content)

        for index, chunk in enumerate(chunks):
            documents.append(
                Document(
                    id=f"{source_doc_id}#{index}",
                    content=chunk,
                    metadata={
                        **metadata,
                        "doc_id": source_doc_id,
                        "chunk_index": index,
                    },
                )
            )

    return documents


def print_results(
    benchmark: dict,
    results: list[dict],
) -> int:
    """In top-3 và trả điểm 0/1/2 cho một câu benchmark."""
    print("\n" + "=" * 80)
    print(f"{benchmark['id']}: {benchmark['question']}")
    print(f"Gold document: {benchmark['gold_doc_id']}")
    print(f"Metadata filter: {benchmark['metadata_filter']}")

    if not results:
        print("Không có kết quả.")
        return 0

    for rank, result in enumerate(results, start=1):
        content_preview = result["content"].replace("\n", " ")[:220]

        print(f"\nTop-{rank}")
        print(f"  doc_id : {result['metadata'].get('doc_id')}")
        print(f"  chunk  : {result['metadata'].get('chunk_index')}")
        print(f"  score  : {result['score']:.4f}")
        print(f"  text   : {content_preview}...")

    top1 = results[0]
    top1_is_gold = top1["metadata"].get("doc_id") == benchmark["gold_doc_id"]

    top1_has_answer = all(
        term.lower() in top1["content"].lower()
        for term in benchmark["required_terms"]
    )

    all_context = "\n".join(result["content"] for result in results)
    context_has_answer = all(
        term.lower() in all_context.lower()
        for term in benchmark["required_terms"]
    )

    if top1_is_gold and top1_has_answer:
        print("\nĐánh giá: 2 điểm — top-1 đúng và chunk chứa đáp án.")
        return 2

    if context_has_answer:
        print("\nĐánh giá: 1 điểm — top-2/top-3 có ngữ cảnh chứa đáp án.")
        return 1

    print("\nĐánh giá: 0 điểm — top-3 không chứa đủ thông tin trả lời.")
    return 0


def run_ab_test(store: EmbeddingStore) -> None:
    """Chạy Q1 có và không có metadata filter."""
    benchmark = BENCHMARKS[0]

    print("\n" + "#" * 80)
    print("A/B TEST — Q1")

    print("\nA. Có metadata_filter={'audience': 'student'}")
    filtered_results = store.search_with_filter(
        benchmark["question"],
        top_k=3,
        metadata_filter={"audience": "student"},
    )

    for rank, result in enumerate(filtered_results, start=1):
        print(
            f"Top-{rank}: "
            f"doc_id={result['metadata'].get('doc_id')}, "
            f"score={result['score']:.4f}"
        )

    print("\nB. Không dùng metadata filter")
    unfiltered_results = store.search(
        benchmark["question"],
        top_k=3,
    )

    for rank, result in enumerate(unfiltered_results, start=1):
        print(
            f"Top-{rank}: "
            f"doc_id={result['metadata'].get('doc_id')}, "
            f"score={result['score']:.4f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=["mock", "local"],
        default="mock",
        help="mock: dùng cho test nhanh; local: embedding đa ngôn ngữ thật",
    )
    args = parser.parse_args()

    if not CORPUS_DIR.exists():
        raise FileNotFoundError(f"Không tìm thấy corpus: {CORPUS_DIR}")

    if args.provider == "local":
        print("Đang dùng LocalEmbedder đa ngôn ngữ.")
        embedding_fn = LocalEmbedder()
    else:
        print("Đang dùng MockEmbedder. Score không phản ánh ngữ nghĩa thật.")
        embedding_fn = _mock_embed

    documents = load_chunked_documents()

    store = EmbeddingStore(
        collection_name="library_benchmark",
        embedding_fn=embedding_fn,
    )
    store.add_documents(documents)

    print(f"\nĐã nạp {len(documents)} chunks từ {CORPUS_DIR}.")

    total_score = 0

    for benchmark in BENCHMARKS:
        results = store.search_with_filter(
            benchmark["question"],
            top_k=3,
            metadata_filter=benchmark["metadata_filter"],
        )
        total_score += print_results(benchmark, results)

    print("\n" + "=" * 80)
    print(f"TỔNG ĐIỂM RETRIEVAL: {total_score}/10")

    run_ab_test(store)


if __name__ == "__main__":
    main()