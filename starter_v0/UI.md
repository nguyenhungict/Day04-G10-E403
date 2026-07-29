# UI — Research Agent (Streamlit)

`app.py` tái sử dụng nguyên `run_model_tool_loop` trong `chat.py`, nên UI và CLI
chạy đúng cùng một vòng lặp model/tool. Không có agent loop riêng cho UI.

## Chạy

```bash
cd starter_v0
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

PASS khi mở được `http://localhost:8501`.

## UI hiển thị gì

| Yêu cầu | Chỗ hiển thị |
|---|---|
| request | bong bóng chat của user |
| response | bong bóng chat của assistant |
| round | tiêu đề expander `Round N — k tool call` |
| tool name | dòng `🔧 <tên tool>` kèm badge ✅/❌ |
| arguments | cột trái của mỗi tool call (JSON) |
| result / error | cột phải của mỗi tool call (JSON) |
| artifact version | sidebar, kèm `prompt_hash` và `tools_hash` rút gọn |

Transcript được ghi sau **mỗi lượt** vào `transcripts/<version>_<provider>_<timestamp>.transcript.json`,
cùng schema với transcript của `chat.py` và có thêm `"surface": "streamlit"`.
Sidebar có nút tải transcript JSON.

## So sánh nhiều version trên cùng một scenario

Sidebar cho phép trỏ `system_prompt` / `tools.yaml` sang snapshot của version cũ:

| Version | Đường dẫn snapshot |
|---|---|
| v0 | `artifacts/versions/v0/system_prompt.md` + `artifacts/versions/v0/tools.yaml` |
| v1 | `artifacts/versions/v1/system_prompt.md` + `artifacts/versions/v1/tools.yaml` |
| v2 | `artifacts/system_prompt.md` + `artifacts/tools.yaml` (bản hiện tại) |

Các snapshot được trích thẳng từ git nên `artifact_version` hiển thị trên UI
khớp đúng với cột `artifact_version` trong `artifacts/version_log.csv`.

Đổi đường dẫn xong nhớ bấm **🔄 Phiên mới** để transcript ghi đúng cấu hình.

## Scenario demo gợi ý

Ba scenario đầu là các case v0 làm sai và đã được sửa từ v1 — chạy lần lượt ở v0
rồi v2 sẽ thấy khác biệt rõ.

1. **Confirm trước khi gửi** — `Đăng bản tin AI hôm nay lên Telegram giúp mình`
   - v0: gọi thẳng `send`, gửi luôn khi chưa được xác nhận.
   - v2: gọi `clarify` với `response_type=yes_no` để hỏi xác nhận trước.

2. **Thiếu thông tin bắt buộc** — `Tóm tắt 5 tweet mới nhất giúp mình`
   - v0: đoán bừa một handle rồi gọi `timeline`.
   - v2: gọi `clarify` hỏi lại tài khoản nào.

3. **Ngoài phạm vi** — `Viết giúp mình một hàm Python để sắp xếp danh sách`
   - v0: vẫn gọi tool.
   - v2: trả lời trực tiếp, không gọi tool.

4. **Routing đúng theo nguồn** — `Tin AI hôm nay có gì đáng chú ý?`
   → `lookup` với `topic=news`, `timeframe=day`.

5. **Multi-turn giữ ràng buộc** — `Lấy 10 tweet mới nhất của Elon Musk`
   → `Cho mình 3 thôi` → `timeline` với `screenname=elonmusk`, `limit=3`.

## Lưu ý

- UI đọc key từ `.env` qua `env_loader.load_lab_env`; **không** commit `.env` và
  không để lộ key trên màn hình khi demo.
- Đổi provider/model/version giữa phiên sẽ hiện cảnh báo vì transcript đã ghi
  cấu hình cũ — bấm **Phiên mới** để tách phiên.
- `Max tool rounds` mặc định 4; tăng lên nếu scenario cần nhiều bước tool nối tiếp.
