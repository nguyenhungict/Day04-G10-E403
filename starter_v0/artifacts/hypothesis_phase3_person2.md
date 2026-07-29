# Phase 3 Person 2 — Hypothesis 2 (v1 -> v2)

## Bối cảnh

Sau v1, `eval_base.json` đã đạt 1.00 (20/20). Không còn failure nào trên base
suite để làm căn cứ cho hypothesis 2, nên Giai đoạn 3 chuyển trọng tâm sang
team eval mới (`data/eval_group.json`, 10 case do Người 5 thiết kế).

Rà soát độ phủ của bộ group eval cho thấy hai lỗ hổng thật:

- `unnecessary_tool` không có case nào (0/10) dù nằm trong `allowed_failure_types`;
- 6/11 tool được khai báo chưa từng bị eval chạm tới, trong đó có `policy`,
  `papers`, `paper_text` và `format`.

Bộ case đã được cân bằng lại để phủ đủ 6 failure type và chạm tới
`papers` / `policy` / `format`.

## Hypothesis 2

Các declaration của `policy`, `papers` và `paper_text` vẫn ở chất lượng starter
(mô tả tiếng Việt một dòng, không nêu ranh giới với `lookup`, không ánh xạ enum
`sort_by` / `policy_area`). Nếu viết lại các declaration này theo đúng chuẩn của
nhóm tool lõi và bổ sung routing rule tương ứng vào `system_prompt.md`, thì agent
sẽ route đúng sang `policy` / `papers` thay vì rơi về `lookup`, và chọn đúng
`sort_by=lastUpdatedDate` cho yêu cầu "mới nhất".

## Thay đổi ở v2

- `tools.yaml`: viết lại description và mô tả tham số cho `policy`, `papers`,
  `paper_text`; nêu rõ ranh giới với `lookup` và cách chọn enum.
- `system_prompt.md`: thêm 2 routing rule (`policy`, `papers` / `paper_text`) và
  2 argument rule (`policy_area`, `sort_by`).

## Kết quả đo được

| Suite | v1 | v2 |
|---|---|---|
| base (20 case) | 1.00 | 1.00 |
| group (10 case) | 1.00 | 1.00 |

Run đối chứng:

- v1 group chạy lại bằng đúng artifacts v1 (`v1+pd174628eb08d+t228faebbfeac`) qua
  cờ `--system-prompt` / `--tools`: `runs/v1_B_group_openrouter_20260729T165434515334.json`
- v2 base: `runs/v2_B_base_openrouter_20260729T165605268024.json`
- v2 group: `runs/v2_B_group_openrouter_20260729T165635542380.json`

## Kết luận trung thực

**Hypothesis 2 không được xác nhận bằng số liệu.** Với model
`openai/gpt-4o-mini`, v1 đã đạt trần 1.00 trên cả hai suite, kể cả trên các case
`G01_papers_latest` và `G02_policy_citation` vốn được thiết kế để nhắm thẳng vào
phần declaration còn mơ hồ. Tên tool (`policy`, `papers`) đủ tự mô tả để model
route đúng ngay cả khi description còn cụt.

Vì vậy v2 nên được ghi nhận là **cải thiện chất lượng artifact, giữ nguyên
accuracy, không gây regression** — chứ không phải một cải thiện đo được.

## Giới hạn và hướng tiếp theo

Bộ eval hiện tại đã bão hòa, nên không còn phân biệt được v1 với v2. Muốn đo
tiếp cần tăng độ khó, ví dụ:

- case buộc gọi song song nhiều tool (`lookup` + `papers` trong cùng một yêu cầu);
- case đối kháng giữa `papers` và `paper_text` khi trong câu vừa có chủ đề vừa có
  arXiv ID;
- case `paper_text` với ID cụ thể (hiện chưa có case nào);
- hạ xuống model nhỏ hơn để tạo lại khoảng cách đo được giữa các phiên bản.

`request_guard` (tool mới của nhóm) vẫn chưa có case nào trong group suite: theo
thiết kế prompt, nó là guardrail chỉ kích hoạt khi không luật trực tiếp nào áp
dụng, nên rất khó dựng case tự nhiên mà không đi ngược chính thiết kế đó.
