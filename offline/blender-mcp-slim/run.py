#!/usr/bin/env python3
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
