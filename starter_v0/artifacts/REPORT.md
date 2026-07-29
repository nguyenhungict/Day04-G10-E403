# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 16:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team:
- Members:
- Provider/model:

## Baseline v0 ghi nhận

- Run file: [starter_v0/runs/v0_B_base_openrouter_20260729T150801391895.json](starter_v0/runs/v0_B_base_openrouter_20260729T150801391895.json)
- Metric baseline: case_accuracy = 0.70, tool_routing_accuracy = 0.70, argument_accuracy = 0.70, multiturn_accuracy = 1.00
- Số case fail: 6/20, tập trung ở missing_info, out_of_scope và wrong_boundary
- Hypothesis đầu tiên: nếu prompt nhấn mạnh rõ quy tắc clarify/confirm/no-tool và ưu tiên routing đúng cho câu hỏi tweet/news/web, lỗi missing_info và wrong_tool sẽ giảm rõ rệt.

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL và tổng hợp thành digest."

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL:

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Prompt cần nhấn mạnh clarify/confirm/no-tool | case_accuracy |  | 0.70 | [starter_v0/runs/v0_B_base_openrouter_20260729T150801391895.json](starter_v0/runs/v0_B_base_openrouter_20260729T150801391895.json) |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | none / unexpected tool call | Agent gọi tool cho câu hỏi ngoài phạm vi | Bắt buộc rule no-tool cho intent ngoài scope |
| R10_missing_handle | missing_info | timeline | Agent thiếu clarify khi handle bị thiếu và gọi tool ngay | Prompt phải yêu cầu hỏi lại trước khi dùng tool |
| R11_missing_url | missing_info | fetch | Agent thiếu clarify cho URL bị thiếu và gọi fetch | Thêm rule ask_user khi thông tin thiếu |
| R12_confirm_before_send | wrong_boundary | send | Agent bỏ qua bước xác nhận trước khi gửi | Nhấn mạnh confirm-before-send trong prompt |
| R13_parallel_web_and_tweets | wrong_tool | timeline | Agent chọn timeline thay vì social_search cho câu hỏi tweet theo chủ đề | Cần routing rõ cho tweet-topic vs user-timeline |
| R14_out_of_scope_coding | out_of_scope | none / unexpected tool call | Agent gọi tool cho câu hỏi coding không liên quan | Dùng rule no-tool cho câu hỏi ngoài scope |

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
