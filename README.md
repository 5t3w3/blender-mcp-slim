# Blender MCP slim – Model Context Protocol server for Blender and LLMs

**MCP** here means the [Model Context Protocol](https://modelcontextprotocol.io/) (tooling for AI assistants such as Claude or Cursor) — not “Master Control Panel”.

This is a **privacy-focused fork with core MCP functionality only** of [BlenderMCP](https://github.com/ahujasid/blender-mcp) by Siddharth Ahuja.

It ships with **zero runtime dependencies** and can run offline once installed.

**What was removed:**
- All telemetry and data collection
- Poly Haven integration
- Sketchfab integration
- Hyper3D Rodin integration
- Hunyuan3D / Tencent integration
- Terms and Conditions (no longer applicable since no data is collected)

**What remains** is the core MCP functionality: connecting Blender to any AI assistant that supports the Model Context Protocol.

## Features

- **Zero runtime dependencies**: Ships with a minimal, self-contained MCP server implementation — no Pydantic, HTTPX, Uvicorn, or other third-party packages are fetched at install or runtime.
- **Two-way communication**: Connect AI assistants to Blender through a socket-based server
- **Object manipulation**: Create, modify, and delete 3D objects in Blender
- **Material control**: Apply and modify materials and colors
- **Scene inspection**: Get detailed information about the current Blender scene
- **Viewport screenshots**: Capture the 3D viewport for visual context
- **Code execution**: Run arbitrary Python code in Blender from the AI assistant

## Components

1. **Blender Addon (`addon.py`)**: Creates a socket server within Blender to receive and execute commands
2. **MCP Server (`src/blender_mcp/server.py`)**: Implements the Model Context Protocol and connects to the Blender addon

## Installation

### Prerequisites

- Blender 3.0 or newer
- Python 3.10 or newer
- uv package manager (used only to launch the server; the package itself has no runtime dependencies)

The server is **fully offline-capable** after installation — `uvx blender-mcp-slim` does not need to download any Python packages at runtime.

**macOS:**
```bash
brew install uv
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then add uv to the user PATH (restart your IDE afterwards):
```powershell
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

Full installation instructions: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

### Environment Variables

- `BLENDER_HOST`: Host address for Blender socket server (default: `localhost`)
- `BLENDER_PORT`: Port number for Blender socket server (default: `9876`)

### Claude Desktop

Go to Claude > Settings > Developer > Edit Config > `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp-slim"
            ]
        }
    }
}
```

### Cursor

**macOS** - Settings > MCP, add:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp-slim"
            ]
        }
    }
}
```

**Windows** - Settings > MCP > Add Server:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "blender-mcp-slim"
            ]
        }
    }
}
```

> Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both.

### Offline / air-gapped installation

Because the server has **zero runtime dependencies**, you can also run it on a machine that has no Internet access and no package manager installed.

A pre-built offline bundle is included in this repository at `offline/blender-mcp-slim/`. To use it:

```bash
# Copy the directory to the offline machine, then run:
python3 blender-mcp-slim/run.py
```

To re-create the bundle after source changes:

```bash
python3 scripts/build_offline_bundle.py
```

You can also run the server directly from a source checkout without installing anything:

```bash
python3 main.py
```

### Installing the Blender Addon

1. Download the `addon.py` file from this repo
2. Open Blender
3. Go to Edit > Preferences > Add-ons
4. Click "Install..." and select the `addon.py` file
5. Enable the addon by checking the box next to "Interface: Blender MCP"

## Usage

1. In Blender, open the 3D View sidebar (press N if not visible)
2. Find the "BlenderMCP" tab
3. Click "Connect to MCP server"
4. Make sure the MCP server is configured in your AI assistant

### Example Commands

- "Create a red metallic sphere above the cube"
- "Get information about the current scene"
- "Make the lighting like a studio setup"
- "Point the camera at the scene and make it isometric"
- "Create a low-poly landscape"

## Communication Protocol

The system uses a JSON-based protocol over TCP sockets:

- **Commands** are sent as JSON objects with a `type` and optional `params`
- **Responses** are JSON objects with a `status` and `result` or `message`

## Security Considerations

- The `execute_blender_code` tool allows running arbitrary Python code in Blender. Always save your work before using it.
- Complex operations might need to be broken down into smaller steps.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Original project Copyright (c) 2025 Siddharth Ahuja.

## Acknowledgements

This is a fork of [BlenderMCP](https://github.com/ahujasid/blender-mcp) by [Siddharth Ahuja](https://github.com/ahujasid). All credit for the original architecture and implementation goes to the original author.
