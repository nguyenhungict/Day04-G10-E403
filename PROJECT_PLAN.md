# Kế hoạch triển khai Day 04 Lab

## 1. Trạng thái hiện tại

Nhóm đã hoàn thành:

- tạo API key cho model provider và các research API cần dùng;
- tạo `starter_v0/.env` và điền các biến môi trường;
- tạo môi trường ảo `.venv`;
- cài dependencies từ `requirements.txt`.

Lưu ý:

- không commit hoặc chia sẻ file `.env`;
- không đưa API key vào source code, report, screenshot hoặc transcript;
- tất cả lệnh chạy agent được thực hiện trong thư mục `starter_v0/`.

## 2. Kiểm tra setup

Mỗi thành viên cập nhật code rồi kích hoạt môi trường:

```bash
git switch main
git pull --ff-only origin main
cd starter_v0
source .venv/bin/activate
```

Người 1 kiểm tra model provider:

```bash
python scripts/preflight_provider.py --provider openrouter
```

Sau đó smoke-test các core API mà nhóm sử dụng:

- Tavily cho `lookup`;
- Firecrawl cho `fetch`;
- RapidAPI cho `timeline` và `social_search`;
- tool mới của nhóm sau khi implementation hoàn tất.

Setup được xem là đạt khi provider preflight và các core smoke test không trả về lỗi.

## 3. Phân chia branch

| Người | Branch | Trách nhiệm chính |
|---|---|---|
| Người 1 | `main` | Tích hợp, chạy v0-v3, quản lý bản chính và nộp bài |
| Người 2 | `prompt` | `system_prompt.md`, `tools.yaml`, hypothesis v1-v3 |
| Người 3 | `new-tool` | `TOOL.md` và implementation của tool mới |
| Người 4 | `tool-test` | Registry, review, smoke-test và QA tool |
| Người 5 | `evaluation` | Team eval, phân tích log và `version_log.csv` |
| Người 6 | `ui` | Streamlit UI, tool trace và transcript |
| Người 7 | `report` | `REPORT.md`, scenario và nội dung demo |

Chỉ Người 1 merge hoặc push trực tiếp vào `main`.

## 4. Tạo branch cá nhân

Mỗi thành viên chạy một lần:

```bash
git switch main
git pull --ff-only origin main
git switch -c <ten-branch>
git push -u origin <ten-branch>
```

Thay `<ten-branch>` bằng branch được phân công.

## 5. Giai đoạn 1 — Baseline v0

### Thứ tự thực hiện

1. Người 1 chạy provider preflight và core smoke test.
2. Người 1 chạy baseline v0:

   ```bash
   cd starter_v0
   python run_eval.py \
     --provider openrouter \
     --version v0 \
     --suite base \
     --eval-cases data/eval_base.json
   ```

3. Người 1 commit run JSON và push `main`.
4. Người 5 pull `main`, đọc log v0, ghi metric và tổng hợp lỗi.
5. Người 5 push kết quả trên branch `evaluation`.
6. Người 1 merge `evaluation`.
7. Người 2 pull `main`, đọc phân tích và xác định hypothesis 1.

### Kết quả cần có

- provider và core API hoạt động;
- run JSON của v0;
- metric baseline;
- danh sách lỗi và hypothesis đầu tiên.

## 6. Giai đoạn 2 — Tool mới và v1

### Thứ tự thực hiện

1. Người 3 pull `main`, tạo thư mục tool, viết `TOOL.md` và implementation.
2. Người 3 push branch `new-tool`.
3. Người 1 review và merge `new-tool`.
4. Người 4 pull `main`, đăng ký tool trong `tools/__init__.py`, review và smoke-test.
5. Người 4 push branch `tool-test`.
6. Người 2 pull `main`, khai báo tool trong `tools.yaml` và sửa prompt theo hypothesis 1.
7. Người 2 push branch `prompt`.
8. Người 1 merge `tool-test`, sau đó merge `prompt`.
9. Người 1 chạy base eval v1 và push run JSON.
10. Người 5 pull v1, so sánh v0 với v1 và cập nhật `version_log.csv`.
11. Người 5 push `evaluation`; Người 1 merge vào `main`.

### Kết quả cần có

- ít nhất một tool mới chạy thật;
- `TOOL.md`, implementation, registry và declaration đồng bộ;
- run JSON của v1;
- evidence so sánh v0 với v1.

## 7. Giai đoạn 3 — Team eval và v2

### Thứ tự thực hiện

1. Người 5 pull `main` và viết `data/eval_group.json`:
   - 5 single-turn cases;
   - 5 multi-turn cases.
2. Người 5 validate đủ đúng 10 cases rồi push `evaluation`.
3. Người 2 đọc lỗi v1, sửa prompt/tool declaration theo hypothesis 2 và push `prompt`.
4. Người 1 merge `evaluation`, sau đó merge `prompt`.
5. Người 1 chạy base eval v2 và push run JSON.
6. Người 5 pull v2, so sánh v1 với v2 và cập nhật `version_log.csv`.
7. Người 5 push `evaluation`; Người 1 merge vào `main`.

### Kết quả cần có

- `eval_group.json` có đúng 10 cases;
- run JSON của v2;
- evidence so sánh v1 với v2;
- version log được cập nhật.

## 8. Giai đoạn 4 — UI và Report A

### Thứ tự thực hiện

1. Người 6 pull bản `main` mới nhất.
2. Người 6 thêm Streamlit vào `requirements.txt`, tạo `app.py` và tái sử dụng `run_model_tool_loop`.
3. Người 6 hiển thị request, response, tool name, arguments, round, result/error và artifact version.
4. Người 6 kiểm tra transcript được lưu, sau đó push branch `ui`.
5. Người 1 merge `ui`.
6. Người 7 pull `main`, viết Report A và chuẩn bị 3-5 scenario demo.
7. Người 7 thêm hướng dẫn test và link UI, sau đó push `report`.
8. Người 1 merge `report`.

### Kết quả cần có

- UI chạy được tại `http://localhost:8501`;
- UI hiển thị đầy đủ tool trace;
- transcript được lưu;
- Report A và scenario demo hoàn chỉnh.

## 9. Giai đoạn 5 — Demo, v3 và Report B

### Thứ tự thực hiện

1. Cả nhóm pull `main` và chạy thử các scenario demo.
2. Người 7 tổng hợp feedback và gửi cho Người 2.
3. Người 2 sửa prompt/tool declaration theo hypothesis 3 và push `prompt`.
4. Người 1 merge `prompt`.
5. Người 1 chạy v3 base eval:

   ```bash
   cd starter_v0
   python run_eval.py \
     --provider openrouter \
     --version v3 \
     --suite base \
     --eval-cases data/eval_base.json
   ```

6. Người 1 chạy v3 group eval:

   ```bash
   python run_eval.py \
     --provider openrouter \
     --version v3 \
     --suite group \
     --eval-cases data/eval_group.json
   ```

7. Người 5 pull v3, chốt metric v0-v3 và hoàn thiện `version_log.csv`.
8. Người 6 pull v3, kiểm tra UI, transcript và link demo.
9. Người 7 pull evidence cuối và hoàn thiện Report B.
10. Từng người push branch của mình; Người 1 merge lần lượt `evaluation`, `ui`, rồi `report`.

### Kết quả cần có

- run JSON của v3 cho base và group suite;
- metric và version log đầy đủ từ v0 đến v3;
- UI và link demo hoạt động;
- Report B dựa trên evidence thật.

## 10. Quy trình Git chung

Trước khi bắt đầu một phần việc:

```bash
git switch main
git pull --ff-only origin main
git switch <ten-branch>
git merge main
```

Sau khi hoàn thành:

```bash
git status
git add <cac-file-duoc-phan-cong>
git commit -m "mô tả ngắn gọn thay đổi"
git push origin <ten-branch>
```

Sau đó báo Người 1 review và merge. Người thực hiện bước tiếp theo phải pull `main` mới nhất trước khi bắt đầu.

Không dùng `git add .` nếu chưa kiểm tra `git status`. Tuyệt đối không add `.env`, `.venv`, cache hoặc file chứa secrets.

## 11. Giai đoạn cuối — Kiểm tra và nộp bài

1. Người 4 kiểm tra tool implementation, registry và declarations.
2. Người 5 kiểm tra đúng 10 team eval cases, đủ run JSON và version log.
3. Người 6 kiểm tra UI, transcript và link truy cập.
4. Người 7 kiểm tra report và toàn bộ evidence.
5. Người 1 kiểm tra lần cuối:
   - có v0, v1, v2 và v3;
   - có tool mới;
   - có UI;
   - có transcript;
   - có Report A và B;
   - không có `.env`, API key, `.venv` hoặc cache.
6. Người 1 push bản `main` cuối và chuẩn bị bài nộp.

## 12. Luồng bàn giao tổng quát

```text
Người đang thực hiện
→ commit và push branch
→ Người 1 review và merge
→ Người tiếp theo pull main
→ bắt đầu bước tiếp theo
```
