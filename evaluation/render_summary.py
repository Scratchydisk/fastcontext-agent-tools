from __future__ import annotations

from html import escape
from typing import Any


def render_svg(summary: dict[str, Any]) -> str:
    checks = summary["checks"]
    passed = sum(1 for check in checks if check["status"] == "pass")
    failed = len(checks) - passed
    wrapper_status = f"{passed}/{len(checks)} checks pass"
    if failed:
        wrapper_status = f"{passed}/{len(checks)} checks pass, {failed} fail"

    check_text = []
    y = 418
    for check in checks:
        label = escape(check["name"].replace("_", " ").title())
        status = escape(check["status"].upper())
        check_text.append(f'<text x="636" y="{y}" class="fine">- {label}: {status}</text>')
        y += 22

    generated = summary["generated_at"].replace("T", " ").replace("+00:00", " UTC")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520" role="img" aria-labelledby="title desc">
  <title id="title">FastContext before and after evaluation summary</title>
  <desc id="desc">A before and after comparison showing direct main-agent repository exploration versus delegated FastContext exploration, plus local wrapper checks.</desc>
  <style>
    .title {{ font: 700 28px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #17202a; }}
    .subtitle {{ font: 400 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #52616b; }}
    .card-title {{ font: 700 18px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #17202a; }}
    .label {{ font: 600 15px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1f2933; }}
    .body {{ font: 400 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #334e68; }}
    .metric {{ font: 700 26px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #0b7285; }}
    .metric-label {{ font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #334e68; }}
    .pill {{ font: 700 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #ffffff; }}
    .fine {{ font: 400 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #52616b; }}
    .note {{ font: 400 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #52616b; }}
  </style>
  <rect width="960" height="520" fill="#f8faf9"/>
  <rect x="24" y="24" width="912" height="472" rx="12" fill="#ffffff" stroke="#d6dde2"/>

  <text x="48" y="68" class="title">FastContext Effect: Before vs After</text>
  <text x="48" y="94" class="subtitle">Generated {generated} - local wrapper checks plus Microsoft-reported impact evidence.</text>

  <rect x="48" y="128" width="386" height="190" rx="10" fill="#fff7ed" stroke="#fed7aa"/>
  <text x="72" y="166" class="card-title">Without FastContext</text>
  <text x="72" y="200" class="body">Main coding agent explores the repo directly.</text>
  <text x="72" y="228" class="body">- Broad reads and searches stay in solver history</text>
  <text x="72" y="254" class="body">- More irrelevant snippets enter the context window</text>
  <text x="72" y="280" class="body">- Solver spends tokens before it can edit or answer</text>

  <rect x="456" y="190" width="48" height="34" rx="17" fill="#334e68"/>
  <text x="471" y="212" class="pill">vs</text>

  <rect x="526" y="128" width="386" height="190" rx="10" fill="#eff6ff" stroke="#bfdbfe"/>
  <text x="550" y="166" class="card-title">With FastContext MCP</text>
  <text x="550" y="200" class="body">Delegated read-only exploration.</text>
  <text x="550" y="228" class="body">- READ / GLOB / GREP</text>
  <text x="550" y="254" class="body">- Compact file-line citations</text>
  <text x="550" y="280" class="body">- Focused evidence for the solver</text>

  <rect x="48" y="346" width="260" height="98" rx="10" fill="#ecfdf5" stroke="#a7f3d0"/>
  <text x="72" y="384" class="metric">+5.5</text>
  <text x="72" y="414" class="metric-label">up to end-to-end score improvement</text>
  <text x="72" y="436" class="fine">Reported by Microsoft FastContext</text>

  <rect x="328" y="346" width="260" height="98" rx="10" fill="#ecfeff" stroke="#a5f3fc"/>
  <text x="352" y="384" class="metric">60.3%</text>
  <text x="352" y="414" class="metric-label">up to fewer main-agent tokens</text>
  <text x="352" y="436" class="fine">Across reported benchmark settings</text>

  <rect x="608" y="346" width="304" height="98" rx="10" fill="#f8fafc" stroke="#cbd5e1"/>
  <text x="636" y="376" class="label">Wrapper checks:</text>
  <text x="636" y="396" class="fine">- {escape(wrapper_status)}</text>
  {''.join(check_text)}

  <text x="48" y="474" class="note">Local evaluation validates wrapper behavior. Model-quality claims remain attributed to Microsoft FastContext.</text>
</svg>
"""
