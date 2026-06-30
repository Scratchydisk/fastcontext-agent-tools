"""Aggregate per-run rows into a per-task WITH-vs-WITHOUT trade table."""
from __future__ import annotations
import statistics


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 3) if xs else None


def medians(rows, arm, task):
    sel = [r for r in rows if r["arm"] == arm and r["task"] == task]
    if not sel:
        return None
    n = len(sel)
    return {
        "n": n,
        "success_pct": round(100 * sum(bool(r["success"]) for r in sel) / n),
        "med_total_tokens": _median([r["input_tokens"] + r["output_tokens"] for r in sel]),
        "med_cost": _median([r.get("cost_usd") for r in sel]),
        "tool_unused": sum(1 for r in sel if arm == "with" and not r.get("used_fastcontext")),
    }


def trade_table(rows) -> str:
    tasks = sorted({r["task"] for r in rows})
    out = ["| task | arm | n | success % | median tokens | median $ | notes |",
           "|---|---|---|---|---|---|---|"]
    for t in tasks:
        for arm in ("without", "with"):
            m = medians(rows, arm, t)
            if not m:
                continue
            note = f"tool not used in {m['tool_unused']}/{m['n']}" if m["tool_unused"] else ""
            out.append(f"| task {t} | {arm} | {m['n']} | {m['success_pct']}% | "
                       f"{m['med_total_tokens']} | {m['med_cost']} | {note} |")
    return "\n".join(out)
