"""Install layout: what ships where.

One manifest, shared by the CLI installer, the shell installer, and the tests
that prove no skill names a reference which fails to resolve after installation.
The previous layout let SKILL.md point at `docs/X.md` files no installer shipped;
this module exists so that cannot recur silently.
"""

from __future__ import annotations

import re
from typing import Dict, Tuple

# Reference docs each skill may load on demand. Keys are skill directory names.
SKILL_REFERENCES: Dict[str, Tuple[str, ...]] = {
    "ooda-controller": (
        "predictive-science.md",
        "blocker-semantics.md",
        "validation-routing.md",
        "visualization.md",
        "routing-vocabulary.md",
    ),
    "ooda": (
        "predictive-science.md",
        "visualization.md",
        "validation-routing.md",
        "documentation-impact.md",
        "runtime-reliability.md",
    ),
}

GROK_SKILLS = ("ooda", "ooda-controller")

# Every reference doc that must be packaged.
ALL_REFERENCES = tuple(sorted({r for refs in SKILL_REFERENCES.values() for r in refs}))

_REF_PATTERN = re.compile(r"`reference/([A-Za-z0-9._-]+\.md)`")


def referenced_files(skill_text: str) -> Tuple[str, ...]:
    """Every `reference/X.md` a skill body names."""
    return tuple(sorted(set(_REF_PATTERN.findall(skill_text))))
