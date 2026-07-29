---
name: request_guard
track: bonus
kind: control
requires_env: []
inputs: [request, mode, max_suggestions]
outputs: [items]
side_effect: false
---
# request_guard

Classifies a user request before the agent chooses a tool.

Use this tool when the request may be missing required details, may be outside
the research agent scope, or may require confirmation before an action such as
send/post/publish. It is a guardrail tool, not a web search or content fetcher.

## Input schema

- `request` (string, required): the user request to inspect.
- `mode` (string, optional, default `research`): analysis mode. Supported value
  is `research`.
- `max_suggestions` (integer, optional, default `3`): maximum number of helper
  suggestions to return.

## Output schema

The tool returns a dictionary with the standard shape:

```json
{
  "tool": "request_guard",
  "error": null,
  "message": "...",
  "items": [
    {
      "title": "Guard verdict",
      "source": "local_rules",
      "summary": "...",
      "classification": "missing_info",
      "recommended_action": "clarify",
      "suggested_tool": "clarify",
      "missing_fields": ["screenname"],
      "requires_confirmation": false,
      "confidence": 0.94,
      "signals": ["tweet_request", "no_named_account"]
    }
  ]
}
```

## Error handling

- The implementation catches all exceptions with `try/except`.
- Invalid or empty requests return a safe dictionary instead of crashing.
- On error, `items` is an empty list and `error` contains the exception type.