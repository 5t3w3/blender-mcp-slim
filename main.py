#!/usr/bin/env python3
"""Standalone entry point for blender-mcp-slim.

This file lets you run the server directly from a source checkout without
installing the package via pip or uv. It adds `src/` to the module search path
and then starts the MCP server.

Usage:
    python3 main.py
"""

import os
import sys

# Make `blender_mcp` importable when running from the repository root without
# installing the package.
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_REPO_ROOT, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from blender_mcp.server import main as server_main


def main() -> None:
    """Entry point for the blender-mcp package."""
    server_main()


if __name__ == "__main__":
    main()
