"""Score one headless `claude -p --output-format stream-json` run."""
from __future__ import annotations
import os, re

# crude path tokens like src/a/b/File.cs or a\b\File.ts
_PATH = re.compile(r"[\w./\\-]+\.[A-Za-z0-9]+")


def score_events(events: list[dict], truth: set[str], truth_dirs: set[str]) -> dict:
    final, usage, cost, turns = "", {}, None, None
    tool_calls: list[str] = []
    for ev in events:
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []) or []:
                if block.get("type") == "tool_use":
                    tool_calls.append(block.get("name") or "")
        elif ev.get("type") == "result":
            final = ev.get("result") or final
            usage = ev.get("usage") or usage
            cost = ev.get("total_cost_usd", cost)
            turns = ev.get("num_turns", turns)
    success = any(b in final for b in truth)
    paths = _PATH.findall(final)
    area = any(os.path.dirname(p).replace("\\", "/").endswith(
        d.replace("\\", "/").lstrip("/")) for p in paths for d in truth_dirs if d) \
        or any(os.path.basename(p) in truth for p in paths)
    return {
        "success": success,
        "area": bool(area),
        "used_fastcontext": any("fastcontext" in n for n in tool_calls),
        "input_tokens": int(usage.get("input_tokens", 0)),
        "output_tokens": int(usage.get("output_tokens", 0)),
        "cost_usd": cost,
        "num_turns": turns,
        "tool_calls": tool_calls,
    }
