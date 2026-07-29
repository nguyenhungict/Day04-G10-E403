from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

load_lab_env(ROOT)


def new_transcript_id(version: str, provider: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "_".join([safe_slug(version), safe_slug(provider), timestamp])


def reset_chat(version: str, provider: str) -> None:
    transcript_id = new_transcript_id(version, provider)
    st.session_state.messages = []
    st.session_state.turns = []
    st.session_state.transcript_id = transcript_id
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def ensure_state(version: str, provider: str) -> None:
    if "messages" not in st.session_state:
        reset_chat(version, provider)


def read_run_evidence() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        summary = payload.get("summary", {})
        rows.append(
            {
                "version": payload.get("version"),
                "suite": payload.get("suite"),
                "accuracy": summary.get("case_accuracy"),
                "routing": summary.get("tool_routing_accuracy"),
                "arguments": summary.get("argument_accuracy"),
                "multiturn": summary.get("multiturn_accuracy"),
                "provider_errors": summary.get("provider_error_cases"),
                "artifact": payload.get("artifact_version"),
                "run_file": path.name,
                "generated_at": payload.get("generated_at"),
            }
        )
    return rows


def save_session_transcript(
    *,
    artifact: Any,
    provider_name: str,
    model: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    transcript = {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": st.session_state.turns[0]["started_at"] if st.session_state.turns else now_iso(),
        "turns": st.session_state.turns,
    }
    write_transcript(st.session_state.transcript_path, transcript)


def render_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds") or []
    with st.expander(
        f"Tool trace · {len(rounds)} round(s) · status={turn.get('status', 'unknown')}",
        expanded=False,
    ):
        if not rounds:
            st.caption("Không có tool call.")
        for round_record in rounds:
            st.markdown(f"**Round {round_record.get('round')}**")
            assistant_text = round_record.get("assistant_text")
            if assistant_text:
                st.caption(assistant_text)
            calls = round_record.get("tool_calls") or []
            results = round_record.get("tool_results") or []
            if not calls:
                st.code("No tool call", language="text")
            for index, call in enumerate(calls):
                st.markdown(f"`{call.get('name')}`")
                st.json(call.get("args") or {})
                if index < len(results):
                    event = results[index]
                    result = event.get("result")
                    if isinstance(result, dict) and result.get("error"):
                        st.error(json.dumps(result, ensure_ascii=False, indent=2, default=str))
                    else:
                        st.json(result)


st.set_page_config(page_title="G10 Research Agent", page_icon="🔎", layout="wide")
st.title("🔎 G10 Research Agent")
st.caption("Research có evidence: web, social, URL, source audit và tool trace.")

with st.sidebar:
    st.header("Runtime")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    version = st.text_input("Artifact version", value="v3")
    model_input = st.text_input("Model override", value="", help="Để trống để dùng model mặc định.")
    history_window = st.slider("History window", min_value=1, max_value=10, value=5)
    max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=6, value=4)
    model = model_input.strip() or None

    ensure_state(version, provider_name)
    if st.button("Bắt đầu transcript mới", width="stretch"):
        reset_chat(version, provider_name)
        st.rerun()

system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(tool_declarations)
artifact = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)

with st.sidebar:
    st.divider()
    st.subheader("Artifact")
    st.code(artifact.artifact_version, language="text")
    st.caption(f"Transcript: {st.session_state.transcript_path.name}")

chat_tab, evidence_tab = st.tabs(["Chat & trace", "Run evidence"])

with chat_tab:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("turn_index"):
                matching = next(
                    (
                        turn
                        for turn in st.session_state.turns
                        if turn.get("turn_index") == message["turn_index"]
                    ),
                    None,
                )
                if matching:
                    render_trace(matching)

    user_text = st.chat_input("Nhập yêu cầu research…")
    if user_text:
        turn_index = len(st.session_state.turns) + 1
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        with st.chat_message("assistant"):
            with st.spinner("Đang chạy agent và tools…"):
                try:
                    provider = make_provider(provider_name)
                    recent_messages = [
                        {"role": item["role"], "content": item["content"]}
                        for item in trim_history(st.session_state.messages, history_window)
                    ]
                    messages = [
                        {"role": "system", "content": system_prompt},
                        *recent_messages,
                    ]
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=model,
                        max_tool_rounds=max_tool_rounds,
                    )
                    turn_record.update(result)
                    assistant_text = result.get("assistant_text") or ""
                    st.markdown(assistant_text)
                except Exception as exc:
                    assistant_text = "Không thể hoàn thành lượt này. Xem error trong trace."
                    turn_record.update(
                        {
                            "status": "provider_error",
                            "assistant_text": assistant_text,
                            "error": f"{type(exc).__name__}: {str(exc)}",
                        }
                    )
                    st.error(turn_record["error"])

        turn_record["ended_at"] = now_iso()
        st.session_state.turns.append(turn_record)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_text,
                "turn_index": turn_index,
            }
        )
        save_session_transcript(
            artifact=artifact,
            provider_name=provider_name,
            model=model,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        st.rerun()

with evidence_tab:
    evidence = read_run_evidence()
    if evidence:
        st.dataframe(
            evidence,
            width="stretch",
            hide_index=True,
            column_order=[
                "version",
                "suite",
                "accuracy",
                "routing",
                "arguments",
                "multiturn",
                "provider_errors",
                "artifact",
                "run_file",
            ],
        )
    else:
        st.info("Chưa có run JSON trong thư mục runs/.")
