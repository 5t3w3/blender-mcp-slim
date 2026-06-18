#!/usr/bin/env python3
"""Build an offline-ready bundle of blender-mcp-slim.

The bundle is a self-contained directory that can be copied to a machine
without Internet, pip, uv, or any other package manager. It contains only
pure Python source files and a small launcher.

Usage:
    python3 scripts/build_offline_bundle.py

Output:
    offline/blender-mcp-slim/
        blender_mcp/       -- copy of src/blender_mcp/
        run.py             -- launcher that starts the MCP server
"""

from __future__ import annotations

import os
import shutil
import sys


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src", "blender_mcp")
OFFLINE_DIR = os.path.join(REPO_ROOT, "offline")
BUNDLE_DIR = os.path.join(OFFLINE_DIR, "blender-mcp-slim")


RUNNER = '''#!/usr/bin/env python3
"""Offline launcher for blender-mcp-slim.

This directory contains everything needed to run the MCP server. No pip, uv,
Internet, or other package manager is required.

Usage:
    python3 run.py
"""

import os
import sys

# Make the bundled `blender_mcp` package importable regardless of cwd.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from blender_mcp.server import main

if __name__ == "__main__":
    main()
'''


def build() -> None:
    if not os.path.isdir(SRC_DIR):
        print(f"ERROR: source directory not found: {SRC_DIR}", file=sys.stderr)
        sys.exit(1)

    # Clean and recreate bundle directory
    if os.path.exists(BUNDLE_DIR):
        shutil.rmtree(BUNDLE_DIR)
    os.makedirs(BUNDLE_DIR, exist_ok=True)

    # Copy package source (ignore cache files and compiled bytecode)
    shutil.copytree(
        SRC_DIR,
        os.path.join(BUNDLE_DIR, "blender_mcp"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )

    # Write launcher
    run_path = os.path.join(BUNDLE_DIR, "run.py")
    with open(run_path, "w", encoding="utf-8") as f:
        f.write(RUNNER)
    os.chmod(run_path, 0o755)

    print(f"Offline bundle created at: {BUNDLE_DIR}")
    print(f"To run on an offline client:")
    print(f"  1. Copy the directory {BUNDLE_DIR} to the target machine")
    print(f"  2. Run: python3 blender-mcp-slim/run.py")


if __name__ == "__main__":
    build()
