"""Blender MCP slim — Model Context Protocol server for Blender and LLMs.

Fork without telemetry and third-party service integrations.
Original project: https://github.com/ahujasid/blender-mcp
"""

__version__ = "1.5.5"

from .server import BlenderConnection, get_blender_connection
