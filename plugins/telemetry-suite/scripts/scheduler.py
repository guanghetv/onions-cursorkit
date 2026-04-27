#!/usr/bin/env python3
"""
兼容入口：显式表示这是第二阶段的 scheduler runtime。
"""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("audit_from_csv.py")), run_name="__main__")
