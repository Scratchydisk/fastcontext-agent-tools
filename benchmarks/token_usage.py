"""Token-usage benchmark: main-agent context, with vs without FastContext.

The value claim is that delegating exploration keeps the search work out of the
main agent's context. For each case we measure tokens that would enter that
context:

- WITH FastContext: the exact JSON the MCP tool hands back (citations + final
  answer + metadata). That is all the main agent ingests per call.
- WITHOUT, "inline search": the tool-result bytes in FastContext's own
  trajectory. This is the identical search work, counted as if the main agent
  had run it itself and read every result into context.
- WITHOUT, "grep + read": an independent baseline — grep the repo for sensible
  terms, read every matching file, count tokens.

Writes results/token_usage.md.

    python benchmarks/token_usage.py
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess

from _common import config_lines, explore
from cases import CASES, TARGET_REPO
from tokenizer import BACKEND, count


def trajectory_tool_tokens(tp: str | None) -> int:
    if not tp or not os.path.exists(tp):
        return 0
    total = 0
    for line in open(tp):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("role") == "tool":
            total += count(ev.get("content") or "")
    return total


def grep_read_tokens(terms: str) -> tuple[int, int]:
    try:
        out = subprocess.run(
            ["rg", "-l", "-i", "-e", terms, TARGET_REPO],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception:
        return 0, 0
    files = [f for f in out.splitlines() if f.strip()][:10]
    total = 0
    for f in files:
        try:
            total += count(open(f, encoding="utf-8", errors="replace").read())
        except OSError:
            pass
    return total, len(files)


def main() -> None:
    rows = []
    for query, _truth, terms in CASES:
        res = explore(TARGET_REPO, query)
        answered = bool(res.get("citations"))
        with_tok = count(json.dumps(res, indent=2, sort_keys=True))
        inline_tok = trajectory_tool_tokens(res.get("trajectory_path"))
        naive_tok, nfiles = grep_read_tokens(terms)
        rows.append(
            {
                "query": query, "answered": answered, "with": with_tok,
                "inline": inline_tok, "naive": naive_tok, "nfiles": nfiles,
            }
        )

    ans = [r for r in rows if r["answered"]]
    def ratio(num, den):
        return f"{num/den:.1f}x" if den else "n/a"
    sum_with = sum(r["with"] for r in ans)
    sum_inline = sum(r["inline"] for r in ans)
    sum_naive = sum(r["naive"] for r in ans)

    lines = [
        "# Token-usage benchmark: with vs without FastContext",
        "",
        f"Run: {datetime.date.today().isoformat()}",
        f"Tokenizer: {BACKEND}",
        "",
        *config_lines(),
        "",
        "All figures are tokens that enter the **main agent's context**.",
        "",
        "| # | answered | WITH (ctx in) | WITHOUT inline-search | WITHOUT grep+read | reduction |",
        "|---|----------|---------------|-----------------------|-------------------|-----------|",
    ]
    for i, r in enumerate(rows, 1):
        red = ratio(r["inline"], r["with"]) if r["answered"] else "—"
        lines.append(
            f"| {i} | {'yes' if r['answered'] else 'no'} | {r['with']} "
            f"| {r['inline']} | {r['naive']} ({r['nfiles']}f) | {red} |"
        )
    lines += [
        "",
        f"**Answered queries ({len(ans)}/{len(rows)}):** "
        f"{sum_with} tokens in WITH, vs {sum_inline} (inline search) / "
        f"{sum_naive} (grep+read) WITHOUT.",
        "",
        f"**Context reduction: {ratio(sum_inline, sum_with)} (inline search), "
        f"{ratio(sum_naive, sum_with)} (grep+read).**",
        "",
        "Only answered queries count toward the reduction: a miss \"saves\" "
        "tokens but returns nothing, so it is not a real saving. This measures "
        "context cost (the mechanism); the ground-truth figure is a real "
        "Claude Code A/B comparing `/cost` on the same task with and without "
        "the tool. Re-run to confirm — sampling makes results vary.",
        "",
    ]
    report = "\n".join(lines)

    out = os.path.join(os.path.dirname(__file__), "results", "token_usage.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(report)
    print(report)
    print(f"written: {out}")


if __name__ == "__main__":
    main()
