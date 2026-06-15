from __future__ import annotations

from typing import Any


def render_svg(summary: dict[str, Any]) -> str:
    checks = summary["checks"]
    rows = []
    width = 860
    y = 122
    for check in checks:
        passed = check["status"] == "pass"
        color = "#1f9d55" if passed else "#c43b3b"
        label = check["name"].replace("_", " ").title()
        duration = check.get("duration_seconds", 0)
        bar_width = max(28, min(460, int(float(duration) * 120) + 44))
        rows.append(
            f'<text x="44" y="{y}" class="label">{label}</text>'
            f'<rect x="286" y="{y - 17}" width="{bar_width}" height="24" rx="4" fill="{color}"/>'
            f'<text x="{304 + bar_width}" y="{y}" class="value">{check["status"].upper()} · {duration}s</text>'
        )
        y += 48
    generated = summary["generated_at"].replace("T", " ").replace("+00:00", " UTC")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="360" viewBox="0 0 {width} 360" role="img" aria-labelledby="title desc">
  <title id="title">FastContext Agent Tools evaluation summary</title>
  <desc id="desc">Wrapper evaluation showing unit tests, MCP smoke test, and generated documentation artifacts.</desc>
  <style>
    .title {{ font: 700 28px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #17202a; }}
    .subtitle {{ font: 400 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #52616b; }}
    .label {{ font: 600 15px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1f2933; }}
    .value {{ font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1f2933; }}
    .note {{ font: 400 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #52616b; }}
  </style>
  <rect width="860" height="360" fill="#f8faf9"/>
  <rect x="24" y="24" width="812" height="312" rx="8" fill="#ffffff" stroke="#d6dde2"/>
  <text x="44" y="68" class="title">FastContext MCP Wrapper Evaluation</text>
  <text x="44" y="94" class="subtitle">Generated {generated}</text>
  {''.join(rows)}
  <text x="44" y="306" class="note">Scope: wrapper protocol, citation parsing, trace output, and path safety.</text>
  <text x="44" y="326" class="note">Model-quality results are cited separately from Microsoft FastContext.</text>
</svg>
"""
