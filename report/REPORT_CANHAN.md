# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đỗ Quốc An
**Nhóm:** phoboi
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity)

**Độ tương tự cosine cao nghĩa là gì?**

Độ tương tự cosine cao, gần 1, cho biết hai vector embedding có hướng gần nhau. Với text embedding, điều này thường có nghĩa là hai câu có nội dung hoặc ngữ nghĩa liên quan.

**Ví dụ có độ tương tự CAO:**

- Câu A: Sinh viên được mượn giáo trình trong 90 ngày.
- Câu B: Thời hạn mượn giáo trình của sinh viên là 90 ngày.
- Tại sao tương đồng: Hai câu diễn đạt cùng một chính sách mượn giáo trình.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Thư viện mở cửa từ 08:00 đến 21:00.
- Câu B: Sinh viên được mượn tối đa 8 cuốn giáo trình.
- Tại sao khác: Một câu nói về giờ phục vụ, câu còn lại nói về hạn mức mượn.

**Tại sao cosine similarity được ưu tiên hơn khoảng cách Euclid cho text embeddings?**

Cosine similarity so sánh hướng của vector nên ít bị ảnh hưởng bởi độ lớn vector. Vì text embedding thường được chuẩn hóa, góc giữa hai vector phản ánh mức liên quan ngữ nghĩa tốt hơn khoảng cách Euclid.

### Bài toán tính toán Chunking

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

> Bước trượt: `500 - 50 = 450` ký tự.  
> Số chunks: `ceil((10000 - 500) / 450) + 1 = ceil(21,11) + 1 = 23`.

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào?**

Bước trượt giảm còn `500 - 100 = 400`, nên số chunk tăng thành `ceil(9500 / 400) + 1 = 25`. Overlap lớn hơn giữ được ngữ cảnh tại ranh giới chunk, nhưng làm tăng số vector cần lưu.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ

**Chiến lược cá nhân:** Tôi chọn **Fixed-size Chunking** với `chunk_size=500` và `overlap=50`. Mỗi chunk có tối đa 500 ký tự; phần overlap 50 ký tự giữ lại ngữ cảnh giữa hai chunk liên tiếp.

**`SentenceChunker.chunk` — hướng tiếp cận:**

Tôi dùng regex `(?<=[.!?])\s+` để tách văn bản sau dấu `.`, `!`, `?`. Sau đó loại bỏ phần rỗng và gom các câu theo `max_sentences_per_chunk`. Với văn bản rỗng hoặc chỉ có khoảng trắng, hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**

Thuật toán ưu tiên tách theo `\n\n`, `\n`, `. `, dấu cách, sau đó mới cắt cứng. Base case là khi đoạn văn không dài hơn `chunk_size`; nếu không còn separator phù hợp thì cắt theo kích thước cố định.

### Lớp EmbeddingStore

**`add_documents` + `search` — hướng tiếp cận:**

Mỗi `Document` được lưu thành record gồm `id`, `content`, `metadata` và `embedding`. Metadata luôn có `doc_id` của tài liệu gốc. Khi tìm kiếm, hệ thống embedding câu hỏi, tính dot product với từng record, sắp xếp điểm giảm dần và lấy `top_k`.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**

`search_with_filter` lọc metadata trước khi tính điểm; ví dụ filter `{"audience": "student"}` loại các tài liệu không dành cho sinh viên. `delete_document` xóa toàn bộ record có `metadata["doc_id"]` bằng mã tài liệu cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer` — hướng tiếp cận:**

Agent truy xuất các chunk liên quan từ `EmbeddingStore`, ghép chúng thành phần `Context`, rồi thêm câu hỏi vào phần `Question`. Prompt yêu cầu LLM chỉ sử dụng thông tin trong context và nói rõ nếu context không đủ.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử

```text
===================================================== test session starts =====================================================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- D:\Thuc hanh AI\K4-Day07-DoQuocAn-2A202602892\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Thuc hanh AI\K4-Day07-DoQuocAn-2A202602892
plugins: anyio-4.15.1
collected 42 items                                                                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                    [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                             [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                      [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                       [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                            [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                            [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                  [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                   [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                 [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                   [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                              [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                          [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                           [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                               [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                         [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                               [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                     [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                       [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                             [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                  [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                    [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                        [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                     [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                              [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                             [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                        [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                    [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                               [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                   [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                         [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                   [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                              [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                             [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                 [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                            [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                     [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED           [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED               [100%]

===================================================== 42 passed in 0.09s ======================================================

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Sinh viên được mượn tối đa 8 giáo trình. | Hạn mức mượn giáo trình là 8 cuốn. | Cao | -0,0250 | Không |
| 2 | Thời hạn mượn giáo trình là 90 ngày. | Giáo trình được gia hạn thêm 30 ngày. | Cao | -0,1095 | Không |
| 3 | Phòng học nhóm mở đến 21:00. | Phòng 111 không phục vụ sáng Thứ Ba. | Thấp | 0,0676 | Có |
| 4 | Gia hạn tài liệu trên OPAC. | Đổi mật khẩu tài khoản thư viện. | Thấp | 0,2425 | Không |
| 5 | Dịch vụ thông tin theo yêu cầu miễn phí cho sinh viên. | Sinh viên được hỗ trợ tìm tài liệu nghiên cứu. | Cao | 0,0849 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 và 2 có nghĩa gần nhau nhưng điểm lại thấp vì kết quả được tính bằng mock embedding. Mock embedding chỉ dùng để kiểm thử pipeline, không biểu diễn tốt ý nghĩa câu; benchmark thật nên dùng embedding đa ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
| - | --------------- | ------------------------------------ | ---------- | ------------------------------ | ------------------------------- |
| 1 | Với giáo trình tại phòng 111, được mượn tối đa bao nhiêu cuốn, trong bao lâu và được gia hạn thế nào? | `student-textbook-borrowing`: quy trình trả tài liệu và lưu ý khi sử dụng thẻ. Tài liệu gold có trong top-3. | 0,0725 | Có liên quan một phần; top-1 chưa chứa chính sách mượn. | Agent nhận context từ tài liệu phòng 111; cần chunk chứa mục Chính sách mượn để trả lời đủ 8 cuốn, 90 ngày và gia hạn 30 ngày. |
| 2 | Chính sách mượn sách tham khảo tại phòng 102 quy định số lượng, thời hạn và gia hạn như thế nào? | `library-account`: hướng dẫn hỗ trợ tài khoản bạn đọc. | 0,3723 | Không | Agent không có context đúng về sách tham khảo phòng 102 nên không trả lời đáng tin cậy. |
| 3 | Phòng học nhóm phục vụ vào thời gian nào và quy trình nhận trả chìa khóa ra sao? | `document-renewal`: hướng dẫn gia hạn tài liệu. | 0,2335 | Không | Agent nhận context không liên quan đến phòng học nhóm. |
| 4 | Khi quên mật khẩu tài khoản thư viện, bạn đọc cần thực hiện các bước nào? | `digital-resource-faq`: hướng dẫn truy cập và đăng nhập tài nguyên số. Tài liệu gold có trong top-3. | 0,3936 | Có liên quan một phần | Agent có context liên quan đến đăng nhập nhưng cần tài liệu `library-account` để nêu đủ các bước reset mật khẩu. |
| 5 | Bạn đọc ngoài HUST có thể đọc toàn văn tài nguyên số không và cần điều kiện gì? | `group-study-room`: thông tin đăng ký và sử dụng phòng học nhóm. Tài liệu gold có trong top-3. | 0,2310 | Không | Agent cần context từ `digital-resource-faq` để trả lời điều kiện đăng ký thẻ hoặc tài khoản thư viện. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **3 / 5**

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

Qua demo, tôi học được rằng cách chia chunk ảnh hưởng trực tiếp đến chất lượng truy xuất: chunk quá ngắn dễ mất ngữ cảnh, còn chunk quá dài có thể chứa nhiều thông tin nhiễu. Tôi cũng thấy metadata filter như `audience: student` hữu ích để giới hạn kết quả đúng đối tượng; với tài liệu có cấu trúc rõ ràng, chunk theo heading có thể giữ trọn ý nghĩa của từng quy định.

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi | 10 / 10 |
| Hoàn thiện code — tests | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất của tôi | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
```