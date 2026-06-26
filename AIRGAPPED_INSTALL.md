# Air-gapped Installation: Blender MCP slim + VS Code + GitHub Copilot

This guide describes how to install `blender-mcp-slim` on a machine that has **no internet access**, including the VS Code + GitHub Copilot setup.

> **Goal:** Run the MCP server on an air-gapped Windows machine and connect it to VS Code + GitHub Copilot.
> The server has **zero runtime dependencies** (no pip, no uv, no internet). Only Python must be installed.

---

## 1. Prepare files on a machine with internet

You need a USB stick or any other removable medium to transfer files to the air-gapped machine.

### 1.1 Get the repository or release bundle

Option A: Clone the repository (if you have access to GitHub on the source machine):

```bash
git clone https://github.com/5t3w3/blender-mcp-slim.git
```

Option B: Download the latest release ZIP from the repository page and extract it.

### 1.2 Copy the offline bundle

Locate the folder:

```
blender-mcp-slim/offline/blender-mcp-slim/
```

Copy this folder to your USB stick. It contains everything needed to run the server offline.

---

## 2. Install Python on the air-gapped machine

Download the **Windows embeddable Python** or the full Python installer from python.org on a machine with internet, then transfer it to the air-gapped machine and install it.

> **Important:** The Python path must be known and absolute, e.g. `C:\Python314\python.exe`. VS Code uses the full path; do not rely on `python` being on the PATH.

---

## 3. Copy the offline bundle to the air-gapped machine

Copy the folder from your USB stick to a permanent location on the air-gapped machine, e.g.:

```
C:\blender-mcp-slim\
```

The directory should look like this:

```
C:\blender-mcp-slim\
├── run.py
└── blender_mcp\
    ├── __init__.py
    ├── server.py
    ├── mcp_minimal.py
    └── ...
```

---

## 4. Install VS Code and GitHub Copilot on the air-gapped machine

### 4.1 VS Code

Download the VS Code installer (`VSCodeUserSetup-x64-...exe`) from the official site on an internet-connected machine, transfer it and install it.

### 4.2 GitHub Copilot

The GitHub Copilot extension requires an internet connection for activation and usage. On an air-gapped machine you have two options:

1. **Copilot via internet proxy (if your air-gapped machine has limited/proxy access):** Install Copilot normally from the Marketplace.
2. **No Copilot activation possible:** Use an alternative that works fully offline, e.g. **Cline**, **Roo Code** or **Continue** with a local model. For VS Code, Cline is a good MCP-capable alternative.

If you can activate Copilot, install the **GitHub Copilot** extension and sign in.

---

## 5. Configure VS Code MCP settings

VS Code + GitHub Copilot reads MCP servers from `mcp.json`. On the air-gapped machine, create the **user-level** file:

```
%APPDATA%\Code\User\mcp.json
```

You can open it with VS Code via:

- `Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)` → open the file
- Or directly create the file above.

Paste this config and adapt the paths to your local Python and the `run.py` you copied:

```json
{
  "servers": {
    "blender": {
      "command": "C:\\Python314\\python.exe",
      "args": [
        "C:\\blender-mcp-slim\\run.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

> **Use absolute paths.** Relative paths may fail because the server process starts with an unpredictable working directory.

Save the file and restart VS Code.

---

## 6. Install and configure Blender on the air-gapped machine

1. Download the Blender installer from `blender.org` on a connected machine, transfer it and install it.
2. Copy the Blender addon `addon.py` from the repository to the air-gapped machine (it is in `blender-mcp-slim/addon.py` in the source repository).
3. In Blender:
   - `Edit` → `Preferences` → `Add-ons` → `Install...`
   - Select `addon.py` and enable it.
4. In the addon preferences (or the 3D Viewport sidebar `N` → `MCP`), set the host to `localhost` and port to `9876`.
5. Start the Blender MCP server in the addon panel (it listens on `localhost:9876`).

---

## 7. Verify the MCP server in VS Code

1. Open VS Code.
2. Open the Copilot chat or panel.
3. Use the command palette (`Ctrl+Shift+P`) and run **Copilot: Show MCP Servers** (or similar, depending on the Copilot version).
4. The server `blender` should be listed and show the 4 tools:
   - `get_scene_info`
   - `get_object_info`
   - `get_viewport_screenshot`
   - `execute_blender_code`

---

## 8. Test it

In the Copilot chat, ask:

```
List the objects in the current Blender scene.
```

The first tool call may require approval. Approve it and the tool should execute.

---

## 9. Troubleshooting

### 9.1 Server logs

The server writes logs to a file by default:

```
C:\blender-mcp-slim\blender_mcp\blender_mcp_server.log
```

Check this file if VS Code reports a timeout or connection error.

### 9.2 Timeout or "server not responding"

- Make sure Blender is running and the addon server is started (`localhost:9876` is listening).
- Make sure all paths in `mcp.json` are absolute and correct.
- Make sure `PYTHONUNBUFFERED=1` is set in the `env` block.
- Restart VS Code after changing `mcp.json`.

### 9.3 Use Cline instead of Copilot (if Copilot cannot be activated offline)

If you cannot activate GitHub Copilot on the air-gapped machine, install **Cline** from a VSIX and use the `cline_mcp_settings.json` included in the repository. Set the same absolute Python and `run.py` paths there.

---

## 10. File checklist for the air-gapped machine

- [ ] Python installed (absolute path known, e.g. `C:\Python314\python.exe`)
- [ ] `C:\blender-mcp-slim\` copied from the offline bundle
- [ ] Blender installed
- [ ] `addon.py` installed and enabled in Blender
- [ ] Blender MCP server started (`localhost:9876`)
- [ ] VS Code installed
- [ ] GitHub Copilot (or Cline) installed
- [ ] `%APPDATA%\Code\User\mcp.json` created with absolute paths
- [ ] VS Code restarted after config change
