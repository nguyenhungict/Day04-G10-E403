# Day 04 Lab v2 Report — G10 Research Agent

## Team

- Team: G10-E403
- Members: 7 thành viên — cập nhật họ tên trước khi nộp chính thức
- Provider/model: OpenRouter / `openai/gpt-4o-mini`
- Final artifact: `v3+pc0e57b1c7965+t84a3f7ce2333`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

G10 Research Agent tìm tin trên web và mạng xã hội, đọc URL, xử lý hội thoại
nhiều lượt, định dạng digest và kiểm tra độ đa dạng nguồn. Agent dừng để hỏi
lại khi thiếu dữ liệu và yêu cầu xác nhận trước hành động gửi/publish.

**Link dùng thử local:** `http://localhost:8501`

Khởi động:

```bash
cd starter_v0
source .venv/bin/activate
streamlit run app.py
```

Chưa tạo public URL vì bản hiện tại được hoàn thiện và kiểm thử local. Khi cần
showdown từ máy khác, chạy Cloudflare Tunnel rồi thay link tại đây.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi thêm dữ liệu hoặc xin xác nhận yes/no | Không |
| `timeline` | Lấy bài đăng gần đây của một tài khoản | Không |
| `social_search` | Tìm bài đăng theo chủ đề | Không |
| `lookup` | Tìm web/general news theo timeframe | Không |
| `fetch` | Đọc nội dung tại URL cụ thể | Không |
| `format` | Định dạng các item đã có thành digest | Không |
| `source_audit` | Kiểm tra URL trùng và độ đa dạng domain nguồn | **Có** |
| `send` | Gửi Telegram sau confirmation | Optional built-in |
| `policy` | Tìm company policy cục bộ | Optional built-in |
| `papers` | Tìm paper trên arXiv | Optional built-in |
| `paper_text` | Tải PDF arXiv và trích text | Optional built-in |

## A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?`
2. `Tìm trên web tin AI hôm nay và tìm thêm tweet về AI.`
3. `Tóm tắt bài này giúp mình: https://example.com/article`
4. `Tóm tắt 5 tweet mới nhất giúp mình.` rồi bổ sung `Của Elon Musk nhé.`
5. `Dùng source_audit kiểm tra https://openai.com/a và https://anthropic.com/b, ngưỡng 2 nguồn.`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback evidence |
|---|---|---|---|
| Thiếu account | `clarify(response_type=text)` | v0 tự đoán `sama`; v1 biết hỏi lại | v0 run + v1 run |
| URL đã có | `fetch(url=...)` | v1 vẫn hỏi lại; v2 mô tả fetch rõ và PASS | v1 R04 + v2 run |
| Audit nguồn | `source_audit(items, min_independent_sources)` | Tool mới phân tích local, không tốn API | transcript turn 1 |
| Telegram boundary | `clarify(response_type=yes_no)` hoặc `send(confirmed=true)` sau xác nhận | v0 gửi ngay; v3 quản lý confirmation state | v0 R12 + v3 runs |
| Multi-source research | `lookup` và `social_search` | v0 dùng sai timeline; v1 trở đi gọi đúng hai tool | v0 R13 + v3 base |

---

# PHẦN B — Chi tiết và bằng chứng

Metric chỉ được dùng khi `provider_error_cases=0` và
`measured_cases=total_cases`. Tất cả run được liệt kê dưới đây thỏa điều kiện
này. Tool result có lỗi vẫn được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | Starter baseline | Prompt khuyến khích đoán dữ liệu sẽ gây sai routing/boundary | Base accuracy | — | 70% | `runs/v0_B_base_openrouter_20260729T150801391895.json` |
| v1 | Scope, missing-info và confirmation trong system prompt | Không đoán handle/URL và hỏi yes/no trước action sẽ sửa phần lớn baseline | Base accuracy | 70% | 95% | `runs/v1_B_base_openrouter_20260729T152202231033.json` |
| v2 | Mô tả tool rõ boundary; thêm `source_audit` | Đưa routing convention vào tool interface sẽ sửa lỗi URL còn lại | Base accuracy | 95% | 100% | `runs/v2_B_base_openrouter_20260729T152420023512.json` |
| v3 | Intent precedence, confirmation state và strict refusal | Explicit intent, proactive confirmation và từ chối không kèm lời giải sẽ sửa group/manual-review failures mà không regression base | Group accuracy | 70% | 100% | `runs/v3_B_group_openrouter_20260729T162735813711.json` |

Final v3 base đạt:

- case accuracy: 100%;
- tool routing accuracy: 100%;
- argument accuracy: 100%;
- multiturn accuracy: 100%;
- provider errors: 0/20.

Evidence: `runs/v3_B_base_openrouter_20260729T162648208908.json`.

Final v3 group đạt 100% trên 10/10 cases và không có provider error.

Lưu ý provenance: v0 do Người 1 chạy trước khi bàn giao và run JSON có
`tools_hash=6cdb53d5d7b8...`, khác snapshot starter được pull sau đó
(`011c271ef0bb...`). Vì artifact v0 gốc không được commit kèm run, kết luận
v0→v1 có thể bị confound một phần bởi tool declaration. Các so sánh v1→v2 và
v2-group→v3-group có artifact/hash được kiểm soát và tái lập từ file hiện tại.

## B2. Failure analysis

| Case ID | Version | Actual tool calls | What failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | v0 | `send` | Gọi action tool để trả lời toán ngoài scope | v1 định nghĩa scope và no-tool behavior |
| `R10_missing_handle` | v0 | `timeline(sama)` | Tự đoán account khi user chưa nêu | v1 bắt buộc `clarify(text)` |
| `R11_missing_url` | v0 | `fetch(example.com/article)` | Tự tạo URL | v1 cấm invent URL |
| `R12_confirm_before_send` | v0 | `send` | Gửi trước confirmation | v1 thêm action boundary |
| `R13_parallel_web_and_tweets` | v0 | `lookup` + `timeline` | Sai query/topic và dùng timeline thay social search | v1 cho phép nhiều tool; v2 mô tả routing |
| `R14_out_of_scope_coding` | v0/manual v3 review | `send`, sau đó no-tool nhưng vẫn đưa code | Routing được sửa ở v1 nhưng strict refusal chưa đạt khi review UI | Final v3 cấm giải bài/cung cấp code sau khi từ chối |
| `R04_read_url_routing` | v1 | `clarify(text)` | URL đã có nhưng vẫn hỏi lại | v2 mô tả rõ `fetch` thắng khi URL hiện diện |
| `G04_missing_article_url` | v2 group | `clarify` thiếu `response_type` | Dựa vào default khiến grader sai args | v3 yêu cầu luôn truyền explicit control args |
| `G05_source_diversity_audit` | v2 group | Hai lần `fetch` | URL cue lấn át audit intent | v3 thêm intent precedence |
| `GM04_send_after_confirmation` | v2 group | `clarify(yes_no)` | Hỏi lại dù user đã xác nhận | v3 nhận proactive confirmation và gọi `send(true)` |

Group case `GM04` ban đầu so khớp nguyên chuỗi có dấu chấm và sinh false
negative dù tool call đúng về nghĩa. Team bỏ assertion dấu câu, tiếp tục chấm
`send` và `confirmed=true`; actual text vẫn được review thủ công trong run.

## B3. Team eval cases

`data/eval_group.json` có đúng 5 single-turn và 5 multi-turn cases.

| Case ID | What it tests | Expected | Final v3 |
|---|---|---|---|
| `G01_account_timeline_limit` | Account routing và limit | `timeline(sama, 2)` | PASS |
| `G02_social_topic_top` | Topic search và Top | `social_search(Gemini, Top)` | PASS |
| `G03_web_news_month` | News timeframe month | `lookup(news, month)` | PASS |
| `G04_missing_article_url` | Không đoán URL | `clarify(text)` | PASS |
| `G05_source_diversity_audit` | Tool mới và threshold | `source_audit(..., 2)` | PASS |
| `GM01_correct_timeline_limit` | Carry account, sửa limit | `timeline(sama, 4)` | PASS |
| `GM02_switch_social_to_web` | Chuyển tool và carry topic | `lookup(AI, news, month)` | PASS |
| `GM03_url_after_clarification` | Dùng URL được bổ sung | `fetch(url)` | PASS |
| `GM04_send_after_confirmation` | Confirmation boundary | `send(confirmed=true)` | PASS |
| `GM05_update_audit_threshold` | Carry items, sửa threshold | `source_audit(..., 3)` | PASS |

Evidence: `runs/v3_B_group_openrouter_20260729T162735813711.json`.

## B4. Live chat evidence

Transcript:
`transcripts/v3_openrouter_20260729T162832007512.transcript.json`.

| Turn | Version | Tool calls + args | Outcome |
|---|---|---|---|
| Audit hai nguồn | v3 | `source_audit(items=[openai.com, anthropic.com], min=2)` | PASS; trả về 2 domain, verdict `diverse` |
| Coding ngoài phạm vi | v3 | Không gọi tool | PASS; từ chối và chỉ định hướng tìm tài liệu, không cung cấp code |
| Yêu cầu đăng Telegram | v3 | `clarify(response_type=yes_no)` | PASS; trạng thái `waiting_for_user`, không live-send |

## B5. Tool capability evidence

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Must-have tool mới: `source_audit` | `tools/source_audit/TOOL.md`, `tool.py`, transcript turn 1 | Registry, declaration, smoke test, audit 2 domain và duplicate URL | Không tuyên bố xác minh factual truth; chỉ đo diversity/duplicate |
| Optional built-in: `send` | v0/v3 eval và transcript turn 3 | Confirmation boundary được kiểm chứng | Telegram credentials để unset trong eval; không live-send |
| Optional built-in: arXiv/policy | Implementation có sẵn | Không dùng để claim core hoặc bonus | Chỉ demo khi có evidence riêng |
| UI core | `app.py` | Chat, round trace, result/error, artifact hash, run table, transcript | Không render secrets |

Nhóm thêm một tool mới nên đáp ứng must-have nhưng không claim bonus hơn ba tool.

Provider preflight PASS với OpenRouter/`openai/gpt-4o-mini` và structured call
`timeline(screenname=sama, limit=1)`. Direct smoke test được lưu tại
`analysis/smoke_test_summary.json`: `lookup`,
`fetch`, `timeline`, `social_search` và `source_audit` đều PASS. Một số tool
result trong lúc chạy eval trước đó có lỗi tạm thời từ Twitter API45 (HTTP 502
hoặc response không phải JSON); direct smoke test sau đó PASS nên đây là lỗi
upstream không ổn định. `GM04` gọi `send` sau confirmation và trả lỗi thiếu
Telegram credentials đúng với cấu hình eval an toàn; nhóm chỉ dùng kết quả đó
để chấm routing/boundary, không claim live-send.

## B6. UI evidence

- `streamlit>=1.30.0` đã được thêm vào `requirements.txt`.
- `app.py` tái sử dụng `run_model_tool_loop` từ `chat.py`.
- Streamlit AppTest render PASS, không có exception.
- Health endpoint `http://localhost:8501/_stcore/health` trả `ok`.
- UI có hai tab: `Chat & trace` và `Run evidence`.
- Public tunnel chưa bật trong bản local.

## B7. Reflection

- Các invariant về scope, missing information, conversation correction và action
  boundary thuộc `system_prompt.md`.
- Điều kiện dùng/không dùng từng tool, argument convention và default quan trọng
  thuộc `tools.yaml`.
- Routing PASS không đảm bảo tool execution PASS; lỗi RapidAPI HTTP 502 cần
  manual review.
- Exact-string assertion cho nội dung tự nhiên dễ tạo false negative. Team eval
  nên chỉ assert field quan trọng cho failure type và review text thủ công.
- Bước tiếp theo: thêm retry/backoff cho Twitter API, cache read-only và test UI
  trên public tunnel bằng thiết bị thứ hai.
