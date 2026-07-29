# Phase 1 Person 2 Hypothesis

## Baseline v0 evidence

- Run file: `runs/v0_B_base_openrouter_20260729T150801391895.json`
- Artifact version: `v0+peb1c8179815b+t6cdb53d5d7b8`
- Measured cases: 20 / 20
- Provider error cases: 0
- Case accuracy: 0.70
- Tool routing accuracy: 0.70
- Argument accuracy: 0.70
- Multiturn accuracy: 1.00

## Failure pattern

The largest failure cluster comes from the baseline prompt telling the agent to avoid asking questions, guess missing inputs, and perform send/publish actions immediately.

Affected cases:

| Case ID | Expected | Actual | Failure |
|---|---|---|---|
| R08_out_of_scope | no tool | send | Unexpected tool call for an out-of-scope math request |
| R10_missing_handle | clarify | timeline | Guessed `sama` instead of asking for the missing account |
| R11_missing_url | clarify | fetch | Guessed `https://example.com/article` instead of asking for the missing URL |
| R12_confirm_before_send | clarify yes/no | send | Sent without explicit confirmation |
| R14_out_of_scope_coding | no tool | send | Unexpected tool call for an out-of-scope coding request |

There is also one routing/schema issue:

| Case ID | Expected | Actual | Failure |
|---|---|---|---|
| R13_parallel_web_and_tweets | lookup + social_search | lookup + timeline | Used `timeline` instead of `social_search`; changed query from `AI` to `AI news`; omitted `topic: news` |

## Hypothesis 1 for v1

If `system_prompt.md` explicitly defines the decision boundaries for missing required information, out-of-scope requests, and confirmation before `send`, then v1 should recover the missing `clarify` and no-tool cases without changing tool implementations.

Recommended v1 change:

- Replace the "never ask, just guess" instruction with a rule to call `clarify` when a required identifier or URL is missing.
- Require `clarify(response_type="yes_no")` before any `send`, post, publish, or external action.
- Return a normal answer without tools for requests outside the research/tool scope.
- Add routing guidance that social keyword searches use `social_search`, while account-specific recent posts use `timeline`.
