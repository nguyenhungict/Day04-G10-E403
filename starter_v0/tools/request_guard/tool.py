from __future__ import annotations

import re
from typing import Any


_RE_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_RE_HANDLE = re.compile(r"@[A-Za-z0-9_]{1,30}")


def _has_any(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def _limit_suggestions(items: list[str], max_suggestions: int) -> list[str]:
    return items[: max(1, int(max_suggestions or 3))]


def request_guard(request: str = "", mode: str = "research", max_suggestions: int = 3) -> dict[str, Any]:
    """Classify a request into a safe routing decision before the agent acts."""

    try:
        cleaned_request = request if isinstance(request, str) else str(request)
        cleaned_request = cleaned_request.strip()
        if not cleaned_request:
            return {
                "tool": "request_guard",
                "error": "ValueError",
                "message": "request is required",
                "items": [],
            }

        normalized = cleaned_request.lower()
        has_url = bool(_RE_URL.search(cleaned_request))
        has_handle = bool(_RE_HANDLE.search(cleaned_request))
        has_send_intent = _has_any(normalized, ("gửi", "gui", "đăng", "dang", "post", "publish", "send"))
        has_tweet_intent = _has_any(normalized, ("tweet", "tweets", "twitter", "x.com", "x "))
        has_web_intent = _has_any(normalized, ("web", "websites", "tin", "news", "bài", "bai", "bài viết", "bai viet", "article", "url", "link"))
        has_code_or_math_intent = _has_any(normalized, ("python", "code", "hàm", "ham", "fibonacci", "tích phân", "tich phan", "nguyên hàm", "nguyen ham", "recursion"))

        classification = "proceed"
        recommended_action = "proceed"
        suggested_tool = "lookup"
        missing_fields: list[str] = []
        requires_confirmation = False
        confidence = 0.61
        signals: list[str] = []
        suggestions: list[str] = []

        if has_send_intent:
            classification = "needs_confirmation"
            recommended_action = "clarify"
            suggested_tool = "clarify"
            requires_confirmation = True
            confidence = 0.97
            signals.extend(["send_intent", "confirmation_required"])
            suggestions.extend([
                "Ask for yes/no confirmation before any send/post/publish action.",
                "Do not call send until the user explicitly confirms.",
            ])

        if has_tweet_intent:
            signals.append("tweet_request")
            if has_handle:
                suggested_tool = "timeline"
                confidence = max(confidence, 0.91)
                signals.append("has_handle")
            else:
                classification = "missing_info"
                recommended_action = "clarify"
                suggested_tool = "clarify"
                missing_fields.append("screenname")
                confidence = 0.95
                signals.append("no_named_account")
                suggestions.extend([
                    "Ask which account the user means.",
                    "If the user wants topic search instead of a specific account, route to social_search.",
                ])

        if has_web_intent:
            signals.append("web_request")
            if has_url:
                suggested_tool = "fetch"
                confidence = max(confidence, 0.92)
                signals.append("has_url")
            elif _has_any(normalized, ("bài này", "bai nay", "this article", "article này", "article nay", "link này", "link nay", "url này", "url nay")):
                classification = "missing_info"
                recommended_action = "clarify"
                suggested_tool = "clarify"
                missing_fields.append("url")
                confidence = 0.96
                signals.append("referenced_article_without_url")
                suggestions.extend([
                    "Ask for the exact URL before calling fetch.",
                    "Do not guess a placeholder link.",
                ])
            else:
                suggested_tool = "lookup"
                confidence = max(confidence, 0.72)

        if has_code_or_math_intent and classification == "proceed":
            classification = "out_of_scope"
            recommended_action = "no_tool"
            suggested_tool = "none"
            confidence = 0.93
            signals.append("outside_research_scope")
            suggestions.extend([
                "Return a plain refusal or scope redirect without tool use.",
                "Do not send a tool call for coding or math requests in this lab scope.",
            ])

        if mode and str(mode).strip().lower() != "research":
            signals.append(f"mode:{mode}")

        item = {
            "title": "Guard verdict",
            "source": "local_rules",
            "summary": (
                "Clarify required" if recommended_action == "clarify" else
                "No tool should be used" if recommended_action == "no_tool" else
                "Proceed with the matched tool"
            ),
            "classification": classification,
            "recommended_action": recommended_action,
            "suggested_tool": suggested_tool,
            "missing_fields": _limit_suggestions(missing_fields, max_suggestions),
            "requires_confirmation": requires_confirmation,
            "confidence": round(confidence, 2),
            "signals": signals,
            "suggestions": _limit_suggestions(suggestions, max_suggestions),
            "normalized_request": cleaned_request,
        }

        return {
            "tool": "request_guard",
            "error": None,
            "message": f"Classified request as {classification}.",
            "items": [item],
        }
    except Exception as exc:
        return {
            "tool": "request_guard",
            "error": type(exc).__name__,
            "message": str(exc),
            "items": [],
        }