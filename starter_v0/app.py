"""Streamlit UI cho Research Agent.

Tái sử dụng nguyên `run_model_tool_loop` từ `chat.py` để UI và CLI chạy đúng
cùng một vòng lặp model/tool, không có nhánh logic riêng cho UI.

Chạy:
    cd starter_v0
    streamlit run app.py
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import (  # noqa: E402  (phải chạy sau khi chèn ROOT vào sys.path)
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402

ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini"]

st.set_page_config(page_title="Research Agent — Day04 G10", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_provider(provider_name: str):
    return make_provider(provider_name)


@st.cache_data(show_spinner=False)
def get_tools(tools_path: str, _mtime: float) -> list[dict[str, Any]]:
    return to_openai_tools(load_tool_declarations(Path(tools_path)))


def new_session(version: str, provider_name: str, model: str | None) -> None:
    """Khởi tạo state + transcript cho một phiên chat mới."""
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), timestamp])

    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.turn_index = 0
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "surface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_tool_trace(turn: dict[str, Any]) -> None:
    """Hiển thị round / tool name / arguments / result hoặc error."""
    rounds = turn.get("rounds") or []
    if not rounds:
        st.caption("Không có tool call nào cho lượt này.")
        return

    for round_record in rounds:
        calls = round_record.get("tool_calls") or []
        results = round_record.get("tool_results") or []
        label = f"Round {round_record['round']} — {len(calls)} tool call"
        if not calls:
            label += " (trả lời trực tiếp, không gọi tool)"
        with st.expander(label, expanded=True):
            if round_record.get("assistant_text"):
                st.markdown("**Assistant text ở round này**")
                st.write(round_record["assistant_text"])

            if not calls:
                continue

            for index, call in enumerate(calls):
                result_event = results[index] if index < len(results) else {}
                result = result_event.get("result", {})
                is_error = isinstance(result, dict) and result.get("error")

                st.markdown(f"**🔧 `{call['name']}`** {'❌ error' if is_error else '✅ ok'}")
                left, right = st.columns(2)
                with left:
                    st.caption("arguments")
                    st.json(call.get("args", {}), expanded=True)
                with right:
                    st.caption("error" if is_error else "result")
                    st.json(result, expanded=False)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.write(turn["user"])

    with st.chat_message("assistant"):
        status = turn.get("status")
        if status == "provider_error":
            st.error(turn.get("error", "provider error"))
        else:
            st.write(turn.get("assistant_text") or "_(không có nội dung trả lời)_")
            if status == "waiting_for_user":
                st.info("Agent đang chờ bạn bổ sung thông tin / xác nhận.")
            elif status == "max_tool_rounds":
                st.warning("Đã chạm giới hạn số round tool.")
        render_tool_trace(turn)


# ----------------------------- Sidebar -----------------------------

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (để trống = mặc định của provider)", value="")
    model = model_input.strip() or None
    version = st.text_input("Version label", value="v2")

    SYSTEM_PROMPT_PATH = Path(
        st.text_input("system_prompt", value=str(ARTIFACTS_DIR / "system_prompt.md"))
    )
    TOOLS_PATH = Path(st.text_input("tools.yaml", value=str(ARTIFACTS_DIR / "tools.yaml")))

    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)
    history_window = st.slider("History window (số cặp lượt giữ lại)", 1, 10, 5)

    st.divider()

    artifacts_ok = SYSTEM_PROMPT_PATH.exists() and TOOLS_PATH.exists()
    if not artifacts_ok:
        st.error("Không tìm thấy system_prompt.md hoặc tools.yaml.")
    else:
        artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
        st.caption("Artifact version")
        st.code(artifact_version.artifact_version, language=None)
        st.caption(f"prompt_hash `{artifact_version.prompt_hash[:12]}`")
        st.caption(f"tools_hash  `{artifact_version.tools_hash[:12]}`")

    if st.button("🔄 Phiên mới", use_container_width=True):
        new_session(version, provider_name, model)
        st.rerun()

st.title("🔎 Research Agent")
st.caption("Day04 · Nhóm G10 · UI dùng chung `run_model_tool_loop` với CLI `chat.py`")

if not artifacts_ok:
    st.stop()

if "transcript" not in st.session_state:
    new_session(version, provider_name, model)

# Đổi provider/model/version giữa chừng sẽ làm transcript không còn nhất quán.
transcript = st.session_state.transcript
if (
    transcript["provider"] != provider_name
    or transcript["model"] != model
    or transcript["version"] != version
):
    st.warning(
        "Provider / model / version đã đổi so với phiên hiện tại. "
        "Bấm **Phiên mới** để transcript ghi đúng cấu hình."
    )

for past_turn in st.session_state.turns:
    render_turn(past_turn)

user_text = st.chat_input("Nhập yêu cầu research…")

if user_text:
    st.session_state.turn_index += 1
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tools = get_tools(str(TOOLS_PATH), TOOLS_PATH.stat().st_mtime)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.spinner("Agent đang chạy tool loop…"):
        try:
            result = run_model_tool_loop(
                provider=get_provider(provider_name),
                messages=messages,
                tools=tools,
                model=model,
                max_tool_rounds=max_tool_rounds,
            )
            turn_record.update(result)
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append(
                {"role": "assistant", "content": result["assistant_text"]}
            )
        except Exception as exc:  # giữ UI sống; lỗi provider là evidence
            turn_record.update(
                {"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"}
            )

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
    st.rerun()

with st.sidebar:
    st.divider()
    st.caption("Transcript")
    path = st.session_state.transcript_path
    st.code(str(path.relative_to(ROOT)), language=None)
    if path.exists():
        st.download_button(
            "⬇️ Tải transcript JSON",
            data=path.read_bytes(),
            file_name=path.name,
            mime="application/json",
            use_container_width=True,
        )
        st.caption(f"{len(st.session_state.turns)} lượt đã ghi")
