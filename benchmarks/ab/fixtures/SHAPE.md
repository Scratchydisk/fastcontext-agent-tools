# headless claude stream-json output shape

Captured with: `claude 2.1.196 (Claude Code)`  
Date: 2026-06-30  
Fixtures: `probe_events.jsonl` (no-tool run), `probe_tool_events.jsonl` (Bash tool run)  
Both files are gitignored — only this SHAPE.md is committed.

---

## Working invocation

```bash
claude -p "<prompt>" \
  --model opus \
  --output-format stream-json \
  --verbose \
  > probe_events.jsonl 2>probe.err
```

All three flags exist verbatim in claude 2.1.196.  
`--dangerously-skip-permissions` required when the prompt triggers tool calls in an unattended context.

---

## Event sequence (typical)

| # | `type`             | `subtype`        | Notes                            |
|---|--------------------|------------------|----------------------------------|
| 0-N | `system`         | `hook_started`   | One per registered hook          |
| N+1 | `system`         | `hook_response`  | Hook completion                  |
| N+2 | `system`         | `init`           | Session initialisation           |
| …  | `assistant`       | —                | One per model turn               |
| …  | `user`            | —                | Tool result (if tool was called) |
| …  | `rate_limit_event`| —                | Rate-limit metadata              |
| last | `result`         | `success`        | **Primary scoring target**       |

---

## `result` event — field paths

```
result.type                              == "result"
result.subtype                           == "success" | "error"
result.is_error                          bool
result.result                            str   ← final answer text
result.num_turns                         int
result.total_cost_usd                    float
result.duration_ms                       int   (wall time)
result.duration_api_ms                   int   (API time)
result.ttft_ms                           int   (time-to-first-token)
result.stop_reason                       str   ("end_turn" etc.)
result.session_id                        str

result.usage.input_tokens                int   (billable input, excl. cache)
result.usage.output_tokens               int
result.usage.cache_creation_input_tokens int
result.usage.cache_read_input_tokens     int
result.usage.service_tier                str
result.usage.iterations[]               list  (per-API-call breakdown)
  .input_tokens
  .output_tokens
  .cache_read_input_tokens
  .cache_creation_input_tokens
  .type                                  == "message"

result.modelUsage.<model-id>.inputTokens            int
result.modelUsage.<model-id>.outputTokens           int
result.modelUsage.<model-id>.cacheReadInputTokens   int
result.modelUsage.<model-id>.cacheCreationInputTokens int
result.modelUsage.<model-id>.costUSD                float
result.modelUsage.<model-id>.contextWindow          int
result.modelUsage.<model-id>.maxOutputTokens        int

result.permission_denials               list
result.terminal_reason                  str   ("completed" | …)
```

### Assertion check (matches brief)

```python
r = result_event
assert "usage" in r        # ✓
assert "result" in r       # ✓ — final text
assert "total_cost_usd" in r  # ✓
assert r["num_turns"] >= 1    # ✓
```

---

## `assistant` event — field paths

```
assistant.type                           == "assistant"
assistant.message.model                  str   (e.g. "claude-opus-4-8")
assistant.message.id                     str
assistant.message.role                   == "assistant"
assistant.message.content[]             list of content blocks
assistant.message.usage.input_tokens    int
assistant.message.usage.output_tokens   int
assistant.session_id                    str
assistant.request_id                    str
```

### Content block types observed

**text block** (always present when model replies):
```json
{
  "type": "text",
  "text": "READY"
}
```

**thinking block** (extended thinking, when enabled):
```json
{
  "type": "thinking",
  "thinking": "...",
  "signature": "..."
}
```

**tool_use block** (when model calls a tool):
```json
{
  "type": "tool_use",
  "id": "toolu_01Je27n1piPzojuwSSeSxznx",
  "name": "Bash",
  "input": {"command": "echo hello", "description": "Print hello"},
  "caller": "..."
}
```

Key field for scorer: `assistant.message.content[].name` (tool name, when `type == "tool_use"`).

---

## `user` event — shape (tool result)

Appears after a tool call; carries the tool output back to the model.

```
user.type    == "user"
user.message.role  == "user"
user.message.content[]  — tool_result blocks
```

---

## Notes for scorer (Task 2)

- **Primary usage source**: `result.usage` (aggregate across all turns)
- **Per-model breakdown**: `result.modelUsage[<model-id>]` — camelCase keys
- **Cost**: `result.total_cost_usd` (float, USD)
- **Tool detection**: filter `assistant` events, iterate `message.content[]`, select blocks where `type == "tool_use"`, read `.name`
- **`--verbose` is required** for the `result` event to include `usage` and `total_cost_usd`; without it the `result` event is absent or stripped
- The `result.usage.iterations[]` array gives per-API-call token counts useful if a run spans multiple turns
- `result.modelUsage` keys are model IDs (e.g. `"claude-opus-4-8"`), not aliases — be prepared for this to vary across runs
