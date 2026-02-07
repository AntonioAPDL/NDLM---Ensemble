#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class ValidationResult:
    name: str
    passed: bool
    equation_refs: str
    details: str
    diagnostics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
