# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** phoboi
**Thành viên:** Trịnh Đức Huy - 2A202602865, Trịnh Hoàng Tùng - 2A202602937, Nguyễn Hoàng Sơn - 2A202602457, Đỗ Quốc An - 2A202602892
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ và hướng dẫn sử dụng Thư viện Đại học Bách khoa Hà Nội (HUST)

**Tại sao nhóm chọn chủ đề này?**
> Bộ tài liệu có các chính sách mượn sách, quy trình gia hạn, quản lý tài khoản, giờ phục vụ, phòng học nhóm và tài nguyên số. Nội dung có nhiều tiêu đề, bước thực hiện và con số cần giữ đúng ngữ cảnh, phù hợp để so sánh bốn chiến lược chunking. Hai tài liệu mượn sách cùng có `audience=student` nhưng khác hạn mức và thời hạn cũng giúp kiểm tra tác dụng và giới hạn của metadata filter.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Câu hỏi thường gặp về tài nguyên số | https://library.hust.edu.vn/vi/node/528 | 2026-09-19 / `not-stated` | 1.537 | `doc_id=digital-resource-faq`, `audience=all`, `category=digital-resources`, `department=library`, `language=vi` |
| 2 | Hướng dẫn gia hạn tài liệu | https://library.hust.edu.vn/vi/node/183 | 2026-09-19 / `not-stated` | 759 | `doc_id=document-renewal`, `audience=all`, `category=renewal`, `department=library`, `language=vi` |
| 3 | Dịch vụ sử dụng phòng học nhóm | https://library.hust.edu.vn/vi/node/1363 | 2026-09-19 / `not-stated` | 1.243 | `doc_id=group-study-room`, `audience=all`, `category=study-room`, `department=library`, `language=vi` |
| 4 | Dịch vụ cung cấp thông tin theo yêu cầu | https://library.hust.edu.vn/vi/node/41 | 2026-09-19 / `not-stated` | 1.414 | `doc_id=information-on-demand`, `audience=all`, `category=research-support`, `department=library`, `language=vi` |
| 5 | Hướng dẫn quản lý tài khoản bạn đọc | https://library.hust.edu.vn/vi/node/49 | 2026-09-19 / `not-stated` | 2.010 | `doc_id=library-account`, `audience=all`, `category=library-account`, `department=library`, `language=vi` |
| 6 | Giờ phục vụ thư viện | https://library.hust.edu.vn/vi/node/416 | 2026-09-19 / `not-stated` | 787 | `doc_id=service-hours`, `audience=all`, `category=hours`, `department=library`, `language=vi` |
| 7 | Hướng dẫn mượn sách tham khảo phòng 102 | https://library.hust.edu.vn/vi/node/502 | 2026-09-19 / `not-stated` | 1.071 | `doc_id=student-reference-book-borrowing`, `audience=student`, `category=borrowing`, `department=library`, `language=vi` |
| 8 | Quy trình mượn trả giáo trình phòng 111 | https://library.hust.edu.vn/vi/node/483 | 2026-09-19 / `not-stated` | 2.131 | `doc_id=student-textbook-borrowing`, `audience=student`, `category=borrowing`, `department=library`, `language=vi` |

Số ký tự được tính bằng `len(content)` sau khi tách frontmatter và `strip()` phần thân. Tổng corpus là 10.952 ký tự. `document_version=not-stated` có nghĩa nguồn không nêu phiên bản; nhóm không tự suy đoán ngày hiệu lực.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

Các tên và thông tin liên hệ hỗ trợ xuất hiện trong corpus là đầu mối nghiệp vụ đã được HUST công khai trên các trang nguồn; nhóm không bổ sung dữ liệu cá nhân hoặc tài khoản thật.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `student-textbook-borrowing` | Định danh tài liệu, đối chiếu gold answer và xóa toàn bộ chunk của một tài liệu. |
| `title` | string | `Quy trình mượn trả giáo trình phòng 111` | Cung cấp tên nguồn rõ ràng khi hiển thị kết quả. |
| `source_url` | string | `https://library.hust.edu.vn/vi/node/483` | Truy vết về nguồn công khai để kiểm chứng. |
| `retrieved_at` | string | `2026-09-19` | Theo dõi ngày thu thập và độ mới của dữ liệu. |
| `document_version` | string | `not-stated` | Ghi nhận tình trạng phiên bản, tránh tự suy đoán hiệu lực. |
| `audience` | string | `student` / `all` | Dùng trong `metadata_filter` để giới hạn đối tượng áp dụng. |
| `department` | string | `library` | Cho phép lọc theo đơn vị khi kho dữ liệu mở rộng. |
| `category` | string | `borrowing`, `hours`, `study-room` | Phân biệt loại dịch vụ có nội dung gần nhau. |
| `language` | string | `vi` | Hỗ trợ lọc ngôn ngữ trong corpus đa ngữ. |
| `chunk_index`, `strategy` | integer, string | `1`, `semantic` | Truy vết vị trí chunk và chiến lược đã sinh chunk trong benchmark. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu với `chunk_size=500`:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `student-textbook-borrowing` | FixedSizeChunker (`fixed_size`) | 5 | 466,2 | Trung bình; chunk đầu cắt giữa dòng chính sách mượn. |
| `student-textbook-borrowing` | SentenceChunker (`by_sentences`) | 12 | 175,6 | Khá; giữ câu nhưng chia quy trình thành nhiều mảnh nhỏ. |
| `student-textbook-borrowing` | RecursiveChunker (`recursive`) | 5 | 423,6 | Khá; giữ các đoạn liên tiếp, nhưng chunk dài nhất 619 ký tự. |
| `library-account` | FixedSizeChunker (`fixed_size`) | 5 | 442,0 | Trung bình; sáu bước reset bị chia qua nhiều chunk. |
| `library-account` | SentenceChunker (`by_sentences`) | 13 | 152,4 | Khá; giữ từng bước nhưng tạo nhiều chunk ngắn. |
| `library-account` | RecursiveChunker (`recursive`) | 5 | 397,8 | Trung bình; tiêu đề reset tách khỏi các bước chi tiết. |
| `digital-resource-faq` | FixedSizeChunker (`fixed_size`) | 4 | 421,8 | Tốt; điều kiện và quyền lợi người ngoài trường nằm cùng chunk. |
| `digital-resource-faq` | SentenceChunker (`by_sentences`) | 7 | 217,3 | Khá; dễ đọc nhưng quyền và điều kiện có thể tách nhau. |
| `digital-resource-faq` | RecursiveChunker (`recursive`) | 4 | 381,0 | Tốt; giữ phần FAQ theo các đoạn gần nhau. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Đỗ Quốc An**
- **Loại chiến lược:** Fixed-size Chunking
- **Mô tả & lý do chọn cho chủ đề này:** Dùng `FixedSizeChunker(chunk_size=500, overlap=50)` làm đường cơ sở có kích thước dự đoán được. Overlap 50 ký tự giảm rủi ro mất nội dung tại ranh giới, nhưng chiến lược vẫn có thể cắt giữa câu hoặc một bước hướng dẫn.
- **Code snippet (nếu custom):** Không custom; dùng `FixedSizeChunker` trong `src/chunking.py`.

**Thành viên 2 — Nguyễn Hoàng Sơn**
- **Loại chiến lược:** Recursive Chunking
- **Mô tả & lý do chọn:** Dùng `RecursiveChunker(chunk_size=500)`, ưu tiên tách theo đoạn, dòng, câu rồi khoảng trắng. Cách này hợp với tài liệu hướng dẫn có cấu trúc đoạn, nhưng bước merge hiện tại khiến một số chunk vượt 500 ký tự.
- **Code snippet (nếu custom):** Không custom; dùng `RecursiveChunker` trong `src/chunking.py`.

**Thành viên 3 — Trịnh Hoàng Tùng**
- **Loại chiến lược:** Heading-based Chunking (custom)
- **Mô tả & lý do chọn:** Tách tại heading cấp `##` và giữ các heading cấp `###` trong mục cha. Chiến lược bảo toàn tốt các mục như “Chính sách mượn” hoặc “Hướng dẫn reset mật khẩu”, nhưng một section dài có thể tạo chunk lớn.
- **Code snippet (nếu custom):**
```python
def heading_chunks(text: str) -> list[str]:
    sections = [
        part.strip()
        for part in re.split(r"(?m)(?=^## )", text)
        if part.strip()
    ]
    if len(sections) > 1 and not sections[0].startswith("## "):
        sections[1] = sections[0] + "\n\n" + sections[1]
        sections = sections[1:]
    return sections
```

**Thành viên 4 — Trịnh Đức Huy**
- **Loại chiến lược:** Semantic Chunking (custom)
- **Mô tả & lý do chọn:** Nhúng từng câu/dòng bằng model local đa ngữ và tách khi cosine similarity giữa hai đơn vị liên tiếp nhỏ hơn 0,5 hoặc khi vượt 500 ký tự. Chiến lược hướng đến ranh giới theo chủ đề, nhưng ngưỡng 0,5 tạo 156 chunk rất ngắn trên corpus Markdown này.
- **Code snippet (nếu custom):**
```python
boundary = (
    previous is not None
    and compute_similarity(previous, vector) < threshold
)
if current and (boundary or len(candidate) > chunk_size):
    chunks.append(current)
    current = ""
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Đỗ Quốc An | Fixed-size Chunking | 9 / 10 | Đủ dữ kiện cho 5/5 câu trong top-3; ổn định và dễ cấu hình. | Cắt giữa từ/câu; câu 3 và 4 phải ghép nhiều chunk. |
| Nguyễn Hoàng Sơn | Recursive Chunking | 8 / 10 | Giữ tốt đoạn và quy trình; câu 3 lấy quy trình top-1, thời gian top-2. | Câu 4 thiếu các bước reset trong top-3; có chunk vượt kích thước mục tiêu. |
| Trịnh Hoàng Tùng | Heading-based Chunking | 9 / 10 | Giữ trọn mục chính sách và sáu bước reset mật khẩu. | Câu 3 thiếu mục thời gian trong top-3; chunk dài nhất 794 ký tự. |
| Trịnh Đức Huy | Semantic Chunking | 4 / 10 | Tìm đúng `doc_id` top-1 cho 5/5 câu; tốt với câu hỏi quyền truy cập tài nguyên số. | Chia quá nhỏ; chỉ đủ gold answer cho câu 1 và 5, một phần câu 4. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Fixed-size là chiến lược ổn định nhất trên năm câu hỏi mới vì cả 5/5 gold answer đều có đủ dữ kiện trong top-3; bốn câu có phần hỗ trợ chính ở top-1. Heading-based tốt hơn cho các mục quy trình khép kín như reset mật khẩu, nên phương án cải thiện phù hợp là tách theo heading trước rồi dùng Recursive cho section quá dài. Kết quả được chạy bằng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` và lưu trong `report/benchmark_results.json` với `mock=false`.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Với giáo trình tại phòng 111, được mượn tối đa bao nhiêu cuốn, trong bao lâu và được gia hạn thế nào? | Tối đa 8 cuốn trong 90 ngày, được gia hạn 1 lần thêm 30 ngày, tổng tối đa 120 ngày. Chạy với `metadata_filter={"audience": "student"}`. | `student-textbook-borrowing`, mục 2 “Chính sách mượn giáo trình”. |
| 2 | Chính sách mượn sách tham khảo tại phòng 102 quy định số lượng, thời hạn và gia hạn như thế nào? | Tối đa 5 cuốn, mượn từ 1 đến 30 ngày và được gia hạn 1 lần thêm 7 ngày. | `student-reference-book-borrowing`, mục 2 “Chính sách mượn sách tham khảo”. |
| 3 | Phòng học nhóm phục vụ vào thời gian nào và quy trình nhận trả chìa khóa ra sao? | Thứ 2–thứ 6: 08h00–21h00; thứ 7 và Chủ nhật: 08h00–16h00. Đăng ký, xuất trình và để lại thẻ tại P.411 để nhận chìa khóa; trả chìa khóa để nhận lại thẻ. | `group-study-room`, mục 2 “Thời gian sử dụng” và mục 3 “Quy trình đăng ký”. |
| 4 | Khi quên mật khẩu tài khoản thư viện, bạn đọc cần thực hiện các bước nào? | Truy cập LibOPAC, chọn Đăng nhập, chọn Quên mật khẩu/Quên mã PIN, nhập mã số thẻ, mở liên kết trong email, nhập hai lần mật khẩu mới và gửi. | `library-account`, mục 1 “Hướng dẫn reset mật khẩu”. |
| 5 | Bạn đọc ngoài HUST có thể đọc toàn văn tài nguyên số không và cần điều kiện gì? | Có. Bạn đọc ngoài HUST cần đăng ký thẻ/tài khoản thư viện; sau khi đăng nhập được đọc toàn văn tài liệu số và tải học liệu mở. | `digital-resource-faq`, Câu 4 và Câu 5. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mượn giáo trình phòng 111 | Fixed-size | Có — top-1 | `student-textbook-borrowing#1`, score 0,664974, chứa đủ bốn con số cần trả lời. |
| 2 | Mượn sách tham khảo phòng 102 | Fixed-size / Recursive | Có — top-1 | Cùng trả `student-reference-book-borrowing#0`, score 0,679896, đủ hạn mức và gia hạn. |
| 3 | Thời gian và chìa khóa phòng học nhóm | Recursive | Có — top-1 và top-2 | `group-study-room#1` chứa quy trình, score 0,555067; `#0` chứa thời gian, score 0,515690. |
| 4 | Reset mật khẩu tài khoản thư viện | Heading-based | Có — top-1 | `library-account#0`, score 0,633434, giữ trọn sáu bước. |
| 5 | Quyền truy cập của bạn đọc ngoài HUST | Fixed-size | Có — top-1 | `digital-resource-faq#2`, score 0,715633, chứa điều kiện và quyền lợi. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, ở câu 1: `metadata_filter={"audience": "student"}` thu hẹp ứng viên từ 8 xuống 2 tài liệu dành cho sinh viên và kết quả local đưa chunk giáo trình đúng lên top-1. Tuy nhiên, cả giáo trình và sách tham khảo đều có `audience=student`, nên nội dung câu hỏi “phòng 111/giáo trình” vẫn cần thiết để phân biệt. Không dùng bộ lọc này cho câu 3–5 vì các tài liệu tương ứng có `audience=all` và sẽ bị loại nếu lọc sai.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Đúng `doc_id` chưa đồng nghĩa với đủ ngữ cảnh: Semantic đưa đúng tài liệu lên top-1 ở 5/5 câu nhưng nhiều top-1 chỉ là tiêu đề.
> - Ranh giới chunk quyết định khả năng trả lời: Heading-based giữ trọn sáu bước reset, còn Fixed-size và Recursive chia thông tin này qua nhiều chunk.
> - Metadata filter giúp giảm không gian tìm kiếm, nhưng không thay thế truy xuất ngữ nghĩa khi nhiều tài liệu cùng có `audience=student`.

**Bài học rút ra khi so sánh trong nhóm:**
> Fixed-size tạo 28 chunk và bao phủ đủ dữ kiện của 5/5 câu trong top-3, trong khi Semantic ở ngưỡng 0,5 tạo 156 chunk và làm mất quan hệ giữa tiêu đề, con số và bước thực hiện. Heading-based phù hợp tài liệu Markdown có cấu trúc rõ, nhưng cần cơ chế chia tiếp section dài để tránh chunk đến 794 ký tự. Vì vậy, chất lượng cần được đánh giá trên nội dung chunk chứ không chỉ dựa vào `doc_id` hay score.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thử pipeline hai tầng: tách theo heading để giữ cấu trúc, sau đó dùng Recursive cho section vượt giới hạn. Với Semantic, nhóm sẽ gom các dòng trong cùng đoạn/mục trước khi tính cosine và chọn threshold trên tập câu hỏi phát triển riêng, không tối ưu trực tiếp trên năm câu đánh giá. Nhóm cũng sẽ bổ sung tài liệu có chính sách riêng cho `faculty` hoặc `staff` để kiểm tra metadata filter rõ hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **36 / 40** |
