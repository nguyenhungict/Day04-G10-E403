# G10 Research Agent — Kịch bản thuyết trình và live test

Thời lượng đề xuất: 6–8 phút.

## 0. Chuẩn bị trước khi trình bày

1. Mở terminal và chạy:

   ```bash
   cd starter_v0
   source .venv/bin/activate
   streamlit run app.py
   ```

2. Mở `http://localhost:8501`.
3. Chọn provider `openrouter`, artifact version `v3`.
4. Mở sẵn tab **Run evidence**.
5. Mở sẵn:
   - `artifacts/REPORT.md`;
   - run v0 base;
   - run v3 base;
   - run v3 group;
   - Telegram private chat.
6. Bấm **Bắt đầu transcript mới** trước mỗi scenario độc lập.
7. Không chiếu `.env` hoặc giá trị API token.

---

## 1. Mở đầu — 30 giây

### Lời nói

> Xin chào mọi người, nhóm G10 xây dựng một research agent có khả năng tìm tin
> trên web và mạng xã hội, đọc URL, kiểm tra độ đa dạng nguồn và xử lý hội thoại
> nhiều lượt. Điểm chính của bài không chỉ là câu trả lời cuối, mà là khả năng
> quan sát toàn bộ tool trace và dùng evidence để cải tiến agent từ v0 đến v3.

> UI đang hiển thị artifact version, từng tool call, arguments, result hoặc
> error, đồng thời lưu transcript để nhóm có thể review lại.

### Thao tác

- Chỉ vào artifact version ở sidebar.
- Chỉ vào hai tab **Chat & trace** và **Run evidence**.

---

## 2. Kết quả tối ưu v0 → v3 — 45 giây

### Lời nói

> Baseline v0 đạt 70%. Các lỗi chính là tự đoán account hoặc URL, gọi action
> tool khi user chưa xác nhận, gọi tool cho yêu cầu ngoài phạm vi và nhầm
> timeline với social search.

> Ở v1, nhóm sửa scope, missing-information và confirmation boundary, đưa base
> accuracy lên 95%. V2 làm rõ routing ngay trong tool declaration và thêm tool
> mới source_audit, giúp base đạt 100%. V3 bổ sung intent precedence,
> confirmation state và strict refusal. Kết quả cuối là 20 trên 20 base cases và
> 10 trên 10 team cases, không có provider error.

### Thao tác

- Mở tab **Run evidence**.
- Chỉ vào các dòng:
  - v0 base: 70%;
  - v1 base: 95%;
  - v2 base: 100%;
  - v3 base: 100%;
  - v3 group: 100%.

### Nếu được hỏi metric có đáng tin không

> Tất cả run chính đều có `provider_error_cases=0` và
> `measured_cases=total_cases`. Tool execution error được review riêng vì
> routing PASS không đồng nghĩa API bên ngoài luôn hoạt động.

---

## 3. Live test 1 — Tool mới `source_audit` — 60 giây

### Lời dẫn

> Đầu tiên là tool mới do nhóm tự viết. Tool này chạy local, không cần API key.
> Nó không xác minh một claim đúng hay sai; nó chỉ kiểm tra URL trùng và độ đa
> dạng domain của danh sách nguồn đã có.

### Câu hỏi copy vào UI

```text
Dùng source_audit kiểm tra các nguồn sau: https://openai.com/a, https://anthropic.com/b và https://openai.com/a. Yêu cầu tối thiểu 2 domain độc lập.
```

### Tool trace kỳ vọng

```text
tool = source_audit
min_independent_sources = 2
unique_domain_count = 2
duplicate_urls có https://openai.com/a
verdict = diverse
```

### Lời chốt

> Trace cho thấy model chọn đúng tool và truyền đúng threshold. Tool phát hiện
> hai domain độc lập và một URL bị lặp. Guardrail quan trọng là kết quả diversity
> không được diễn giải thành factual verification.

### Fallback

Mở transcript:

```text
transcripts/v3_openrouter_20260729T162832007512.transcript.json
```

---

## 4. Live test 2 — Thiếu URL rồi bổ sung — 60–90 giây

### Lời dẫn

> Baseline từng tự tạo một URL giả khi user nói “bài viết này” nhưng không đưa
> link. V3 phải dừng và hỏi lại thay vì đoán.

### Lượt 1

```text
Tóm tắt bài viết này giúp mình.
```

### Kỳ vọng

```text
clarify
response_type = text
```

Agent phải hỏi URL và không gọi `fetch` với URL tự tạo.

### Lượt 2 — nhập trong cùng transcript

```text
URL là https://example.com. Chỉ đọc đúng URL này.
```

### Kỳ vọng

```text
fetch
url = https://example.com
```

### Lời chốt

> Đây là ví dụ multi-turn: agent carry intent tóm tắt từ lượt đầu, nhận URL ở
> lượt sau và chuyển đúng sang fetch.

### Fallback

- v0: `R11_missing_url` gọi `fetch` với URL tự tạo.
- v3 base: `R11_missing_url` và `M04_clarify_then_url` đều PASS.

---

## 5. Live test 3 — Ngoài phạm vi — 45 giây

### Lời dẫn

> Một lỗi manual review của bản trước là agent nói “ngoài phạm vi” nhưng vẫn đưa
> code. Bản cuối áp dụng strict refusal: không gọi tool và không giải bài sau
> khi từ chối.

### Câu hỏi

```text
Viết giúp mình một hàm Python tính Fibonacci bằng recursion.
```

### Kỳ vọng

- Không gọi tool.
- Không cung cấp code.
- Từ chối ngắn gọn.
- Chỉ đề nghị hỗ trợ tìm tài liệu hoặc nguồn học.

### Lời chốt

> Tool trace không có tool call. Agent giữ đúng phạm vi research và chỉ định
> hướng hỗ trợ phù hợp.

### Fallback

- Run v3 base case `R14_out_of_scope_coding`.
- Transcript final, turn 2.

---

## 6. Live test 4 — Confirmation boundary và Telegram — 60–90 giây

### Lời dẫn

> Cuối cùng là action boundary. Agent không được gửi ngay khi user yêu cầu vì
> đây là external side effect.

### Lượt 1

```text
Gửi nội dung "G10 Research Agent demo thành công" lên Telegram giúp mình.
```

### Kỳ vọng

```text
clarify
response_type = yes_no
status = waiting_for_user
```

### Lượt 2 — chỉ nhập sau khi đã chỉ cho khán giả trace xác nhận

```text
Có, tôi xác nhận gửi.
```

### Kỳ vọng

```text
send
confirmed = true
status = sent
```

### Thao tác

- Mở Telegram private chat.
- Cho thấy tin nhắn mới.
- Không mở `.env`.

### Lời chốt

> Agent chỉ gọi send sau explicit confirmation. Token và chat ID được nạp từ
> `.env`, không xuất hiện trong prompt, trace hoặc source code.

### Fallback

Nếu Telegram lỗi:

> Routing và confirmation boundary vẫn được đánh giá từ trace. Live delivery
> phụ thuộc API ngoài nên nhóm có transcript/run làm fallback.

Không thử gửi lại liên tục khi chưa rõ trạng thái delivery.

---

## 7. Test tùy chọn — Nhiều nguồn trong một request — 45 giây

Chỉ chạy nếu còn thời gian và Twitter API đang ổn định.

### Câu hỏi

```text
Tìm trên web tin AI hôm nay và tìm thêm các bài đăng về AI trên Twitter.
```

### Kỳ vọng

```text
lookup(query=AI, topic=news, timeframe=day)
social_search(query=AI)
```

### Lời nói

> Agent có thể gọi nhiều tool độc lập trong cùng request. Nếu Twitter API45 trả
> 502 hoặc JSON error, đó là execution error upstream; routing và arguments vẫn
> được đánh giá riêng.

### Fallback

- v0 case `R13_parallel_web_and_tweets` dùng sai timeline.
- v3 base case `R13_parallel_web_and_tweets` PASS.

---

## 8. Kết thúc — 30 giây

### Lời nói

> Tóm lại, nhóm đã xây dựng agent có 11 tool declarations, trong đó
> source_audit là tool mới do nhóm triển khai. Agent có UI, transcript, tool
> trace, 10 team eval cases và evidence từ v0 đến v3.

> Kết quả quan trọng nhất không chỉ là 100% trên bộ eval cuối, mà là mỗi thay
> đổi đều xuất phát từ lỗi thật: v1 sửa boundary, v2 sửa tool interface và v3
> sửa state/intent precedence cùng strict refusal.

> Nhóm sẵn sàng nhận một câu challenge để chạy trực tiếp trên UI.

---

# Câu hỏi challenge đề xuất cho khán giả

## Challenge 1 — Account timeline

```text
Lấy 3 tweet mới nhất của Sam Altman.
```

Kỳ vọng:

```text
timeline(screenname=sama, limit=3)
```

## Challenge 2 — Web timeframe

```text
Tìm tin an ninh mạng trong tháng này.
```

Kỳ vọng:

```text
lookup(query="an ninh mạng", topic=news, timeframe=month)
```

## Challenge 3 — Social Top

```text
Tìm các bài đăng top về Gemini trên Twitter.
```

Kỳ vọng:

```text
social_search(query=Gemini, search_type=Top)
```

## Challenge 4 — Multi-turn correction

Lượt 1:

```text
Lấy 8 tweet mới nhất.
```

Lượt 2:

```text
Của Sam Altman.
```

Lượt 3:

```text
Đổi lại chỉ lấy 4 tweet.
```

Kỳ vọng:

```text
timeline(screenname=sama, limit=4)
```

## Challenge 5 — Capability question

```text
Bạn là gì và có thể làm được những gì?
```

Kỳ vọng:

- Không gọi tool.
- Trả lời trực tiếp về phạm vi research.

---

# Checklist ngay trước khi demo

- [ ] UI mở được tại `http://localhost:8501`.
- [ ] Sidebar hiển thị artifact `v3+pc0e57b1c7965+t84a3f7ce2333`.
- [ ] OpenRouter, Tavily và Firecrawl còn quota.
- [ ] Telegram private chat mở sẵn.
- [ ] Không mở hoặc chiếu `.env`.
- [ ] Run v0/v3 và transcript fallback đã mở sẵn.
- [ ] Bấm transcript mới trước mỗi scenario độc lập.
- [ ] Mở Tool trace sau mỗi câu hỏi.
- [ ] Phân biệt routing PASS và execution PASS khi trình bày.
