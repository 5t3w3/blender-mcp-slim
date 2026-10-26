"""Blender MCP slim — Model Context Protocol server for Blender and LLMs.

Fork without telemetry and third-party service integrations.
Original project: https://github.com/ahujasid/blender-mcp
"""

__version__ = "2.0.0"

from .server import BlenderConnection, get_blender_connection
