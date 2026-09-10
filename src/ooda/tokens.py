"""Offline token-equivalent estimator.

CI must never depend on downloading a tokenizer, so this is a deterministic
approximation, not a real BPE count. It reproduces the cl100k pre-tokenizer's
splitting behaviour closely enough to guard a size budget, and it is stable
across runs and machines, which is the property a regression guard needs.

Reported as a band: `lo` is the pre-token count (a tight lower bound for English
prose, since most common words are one token), `hi` adds a conservative
sub-word split model for long tokens.
"""

from __future__ import annotations

import re
from typing import Tuple

# Approximation of the cl100k pre-tokenizer using only `re` (no `regex`
# dependency): contractions, words, short digit runs, punctuation, whitespace.
_PAT = re.compile(
    r"'(?:[sdmt]|ll|ve|re)"
    r"|[^\W\d_]+"
    r"|\d{1,3}"
    r"|[^\s\w]+"
    r"|\s+",
    re.UNICODE,
)

_SUBWORD_CHARS = 6


def estimate(text: str) -> Tuple[int, int]:
    """Return (lo, hi) token-equivalents for `text`."""
    pretokens = [t for t in _PAT.findall(text) if t.strip() or "\n" in t]
    lo = len(pretokens)
    extra = 0
    for token in pretokens:
        stripped = token.strip()
        if len(stripped) > _SUBWORD_CHARS:
            extra += (len(stripped) - 1) // _SUBWORD_CHARS
    return lo, lo + extra


def estimate_hi(text: str) -> int:
    return estimate(text)[1]
