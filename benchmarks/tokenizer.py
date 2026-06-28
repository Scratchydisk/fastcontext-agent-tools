"""Token counting for the benchmarks.

The figure we care about is *tokens that enter the main agent's context* — and
the main agent is Claude. So the most appropriate measure is Anthropic's own
token counter, used when an ``ANTHROPIC_API_KEY`` is available. For offline runs
we fall back to a local ``tiktoken`` encoding (``o200k_base``), and finally to a
crude characters/4 estimate. The chosen backend is reported alongside results so
the numbers are interpretable.

Absolute counts differ slightly between tokenizers; the *ratio* between the
with- and without-FastContext arms is what matters and is stable across them.
"""
from __future__ import annotations

import os


def _anthropic_counter():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
    except ModuleNotFoundError:
        return None
    client = anthropic.Anthropic(api_key=key)
    model = os.getenv("ANTHROPIC_COUNT_MODEL", "claude-sonnet-4-6")

    def count(text: str) -> int:
        if not text:
            return 0
        resp = client.messages.count_tokens(
            model=model, messages=[{"role": "user", "content": text}]
        )
        return resp.input_tokens

    return f"anthropic count_tokens ({model})", count


def _tiktoken_counter():
    try:
        import tiktoken
    except ModuleNotFoundError:
        return None
    enc = tiktoken.get_encoding("o200k_base")
    return "tiktoken o200k_base", (lambda t: len(enc.encode(t or "")))


def _approx_counter():
    return "approx (chars/4)", (lambda t: max(1, len(t or "") // 4))


def get_counter():
    """Return (backend_name, count_fn), preferring the most accurate available."""
    for factory in (_anthropic_counter, _tiktoken_counter, _approx_counter):
        chosen = factory()
        if chosen:
            return chosen


BACKEND, count = get_counter()
