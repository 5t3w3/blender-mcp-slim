# Blender MCP slim – Installation für VS Code + GitHub Copilot, VSCodium und Kilo Code

Dieses Dokument beschreibt, wie der `blender-mcp-slim` MCP-Server unter Windows eingerichtet wird.

**Primäres Ziel:** Air-gapped Rechner mit **VS Code + GitHub Copilot** (kein Nachinstallieren von Dependencies möglich).
**Sekundäre Variante:** Dieser Rechner hier mit **VSCodium + Kilo Code**.

Der Server hat **keine Runtime-Dependencies** und funktioniert daher auch auf air-gapped Rechnern, sobald Python installiert ist.

> **Wichtiger Sicherheitshinweis:** Der Server stellt das Tool `execute_blender_code` bereit, mit dem beliebiger Python-Code in Blender ausgeführt werden kann. Speichere deine Blender-Datei vor der Nutzung und verwende das Tool nur, wenn du der generierten Code-Ausführung vertraust.

---

## Voraussetzungen

- **Python 3.10 oder neuer** (auf dem Zielrechner installiert).
- **Blender 3.0 oder neuer** mit installiertem `addon.py` (siehe `README.md` → *Installing the Blender Addon*).
- Eine der folgenden IDE-Kombinationen:
  - **VS Code** mit **GitHub Copilot**-Extension (primäres Ziel),
  - **VSCodium** mit GitHub Copilot (manuell installiert), **Cline**, **Roo Code** oder **Continue**,
  - **VSCodium** mit **Kilo Code** (diese Variante auf dem aktuellen Rechner).

### Empfohlene Umgebungsvariable

Setze für stdio-Pipes `PYTHONUNBUFFERED=1`, damit Python stdout nicht puffert. Das ist optional, aber empfohlen, besonders unter Windows.

---

## 1. VS Code + GitHub Copilot

### 1.1 Konfigurationspfad

GitHub Copilot in VS Code liest MCP-Server aus einer `mcp.json`. Du hast zwei Möglichkeiten:

| Geltungsbereich | Pfad |
|-----------------|------|
| **Workspace** (projektspezifisch) | `<Workspace>\.vscode\mcp.json` |
| **User** (global) | `%APPDATA%\Code\User\mcp.json` |

> Relative Pfade zur Python-Executable oder zum Skript können je nach Arbeitsverzeichnis des Server-Prozesses scheitern. Verwende daher **absolute Pfade**.

### 1.2 Beispiel-Config (Workspace)

Erstelle `.vscode\mcp.json` im Repository-Wurzelverzeichnis oder in deinem Workspace:

```json
{
  "servers": {
    "blender": {
      "command": "C:\\Users\\stefa\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
      "args": [
        "C:\\Users\\stefa\\Sync\\code-agent\\mcp_slim_outback\\main.py"
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

Passe die Pfade an dein System an:
- `command`: Absolute Pfad zur `python.exe`.
- `args[0]`: Absolute Pfad zu `main.py` (Source-Checkout) oder zu `offline/blender-mcp-slim/run.py` (Offline-Bundle).

### 1.3 Offline-Variante

Für air-gapped Rechner kopiere den Ordner `offline/blender-mcp-slim/` auf den Zielrechner und verwende:

```json
{
  "servers": {
    "blender": {
      "command": "C:\\PFAD\\ZU\\python.exe",
      "args": [
        "C:\\PFAD\\ZU\\blender-mcp-slim\\run.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Es werden keine weiteren Downloads oder Paketmanager benötigt.

### 1.4 Verifizierung

1. Starte Blender und aktiviere das Blender-MCP-Addon.
2. Öffne die Command Palette in VS Code (`Ctrl+Shift+P`) und wähle **Copilot: Show MCP Servers** (oder ähnlich, je nach Extension-Version).
3. Der Server `blender` sollte gelistet sein und die Tools anzeigen (`get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`).
4. Frage Copilot z. B.: *"List the objects in the current Blender scene."*

---

## 2. VSCodium

### 2.1 Hinweis zu GitHub Copilot

GitHub Copilot ist im **Open-VSX-Marketplace** nicht offiziell verfügbar (Microsoft-Lizenz). In VSCodium gibt es zwei Szenarien:

1. **Copilot manuell installieren:** VSIX von Microsoft herunterladen und installieren (`Ctrl+Shift+P` → `Extensions: Install from VSIX`). Anschließend verwendest du die gleiche `mcp.json` wie unter VS Code.
2. **Alternative AI-Extension nutzen:** Verwende eine Extension, die MCP-Server unterstützt, z. B.:
   - **Cline**
   - **Roo Code**
   - **Continue**
   - oder VSCodium-eigene Agenten-Features (sofern vorhanden).

### 2.2 Konfigurationspfad

| Geltungsbereich | Pfad |
|-----------------|------|
| **Workspace** | `<Workspace>\.vscode\mcp.json` |
| **User** (global) | `%APPDATA%\VSCodium\User\mcp.json` |

### 2.3 Beispiel-Config (User-Profil)

Erstelle `%APPDATA%\VSCodium\User\mcp.json`:

```json
{
  "servers": {
    "blender": {
      "command": "C:\\Users\\stefa\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
      "args": [
        "C:\\Users\\stefa\\Sync\\code-agent\\mcp_slim_outback\\main.py"
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

Passe die Pfade an dein System an. Für das Offline-Bundle verwende `offline/blender-mcp-slim/run.py` als Argument.

### 2.4 Empfohlene Extension: Cline

**Cline** ist eine kostenlose AI-Coding-Agent-Extension mit MCP-Unterstützung und im Open-VSX-Marketplace verfügbar (Extension-ID: `saoudrizwan.claude-dev`).

#### Cline in VSCodium installieren

1. VSCodium öffnen.
2. `Ctrl+Shift+X` (Extensions).
3. Auf das Zahnrad-Symbol / die Quellen-Auswahl klicken und sicherstellen, dass **Open VSX Registry** aktiviert ist.
4. Nach `Cline` suchen und **Cline** (`saoudrizwan.claude-dev`) installieren.
5. VSCodium neu starten.

#### MCP-Server in Cline konfigurieren

1. Cline-Panel öffnen (Icon in der linken Seitenleiste).
2. Oben im Cline-Panel auf das **MCP Servers**-Icon (gestapelte Server) klicken.
3. Tab **Configure** wählen.
4. Auf **Configure MCP Servers** klicken. Cline öffnet die Datei `cline_mcp_settings.json`.
5. Den Inhalt der beigefügten `cline_mcp_settings.json` aus diesem Repo kopieren und unter `mcpServers` einfügen.

Für diesen Rechner sieht die Config so aus:

```json
{
  "mcpServers": {
    "blender": {
      "command": "C:\\Users\\stefa\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
      "args": [
        "C:\\Users\\stefa\\Sync\\code-agent\\mcp_slim_outback\\main.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Passe die Pfade an dein System an. Für das Offline-Bundle verwende `offline/blender-mcp-slim/run.py` als Argument.

#### Verifizierung

1. Stelle sicher, dass Blender läuft und das Blender-MCP-Addon aktiviert ist.
2. Im Cline-Panel sollte der Server `blender` mit einem grünen Punkt erscheinen.
3. Die 4 Tools sollten gelistet sein: `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`.
4. Frage Cline: *"List the objects in the current Blender scene."*

### 2.5 Weitere Alternativen

- **Roo Code:** Ähnlich wie Cline, MCP-Config meist in `roo_code_settings.json`.
- **Continue:** Config in `config.json` unter `mcpServer`.
- **GitHub Copilot:** Nur via manuell installiertem VSIX möglich; dann gleiche `mcp.json` wie unter VS Code.

---

## 3. Kilo Code (VSCodium)

**Kilo Code** (auf diesem Rechner in VSCodium installiert) hat native MCP-Unterstützung und benötigt keinen GitHub Copilot.

### 3.1 Konfigurationspfad

Kilo Code liest die MCP-Config aus einer `kilo.jsonc` (JSON with Comments). Du hast zwei Möglichkeiten:

| Geltungsbereich | Pfad |
|-----------------|------|
| **Workspace** | `<Workspace>\kilo.jsonc` oder `<Workspace>\.kilo\kilo.jsonc` |
| **Global** | `~/.config/kilo/kilo.jsonc` |

Die Workspace-Config hat Vorrang vor der globalen Config.

### 3.2 Beispiel-Config (Workspace)

Ich habe die Datei `.kilo\kilo.jsonc` in diesem Repository bereits angelegt:

```jsonc
{
  "mcp": {
    "blender": {
      "type": "local",
      "command": [
        "C:\\Users\\stefa\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
        "C:\\Users\\stefa\\Sync\\code-agent\\mcp_slim_outback\\main.py"
      ],
      "environment": {
        "PYTHONUNBUFFERED": "1",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "enabled": true,
      "timeout": 10000
    }
  }
}
```

**Wichtig:** Bei `command` ist das erste Element die Executable und alle weiteren Elemente sind Argumente. Passe die Pfade an dein System an.

Für das Offline-Bundle verwende:

```jsonc
{
  "mcp": {
    "blender": {
      "type": "local",
      "command": [
        "C:\\PFAD\\ZU\\python.exe",
        "C:\\PFAD\\ZU\\blender-mcp-slim\\run.py"
      ],
      "environment": {
        "PYTHONUNBUFFERED": "1",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "enabled": true,
      "timeout": 10000
    }
  }
}
```

### 3.3 Alternative: Konfiguration über die Kilo-UI

1. Kilo-Icon in der Seitenleiste anklicken.
2. **Einstellungen** (Zahnrad) öffnen.
3. **Agent Behaviour** → **MCP Servers**.
4. Auf **Add Server** klicken.
5. **Local (stdio)** wählen.
6. Befehl und Argumente eintragen:
   - Command: `C:\Users\stefa\AppData\Local\Python\pythoncore-3.14-64\python.exe`
   - Args: `C:\Users\stefa\Sync\code-agent\mcp_slim_outback\main.py`
7. Optional: `PYTHONUNBUFFERED=1`, `BLENDER_HOST=localhost`, `BLENDER_PORT=9876` als Environment-Variablen setzen.

### 3.4 Verifizierung

1. Blender starten und das Blender-MCP-Addon aktivieren.
2. VSCodium neu starten (Kilo Chat reicht meist nicht, weil die Config beim Start eingelesen wird).
3. Kilo erkennt die 4 Tools automatisch: `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `execute_blender_code`.
4. Frage Kilo: *"List the objects in the current Blender scene."*
5. Die erste Tool-Ausführung muss im **Permission Dock** genehmigt werden (oder "Always Allow" wählen).
6. Falls Kilo weiterhin mit `Operation timed out after 10000ms` abstürzt: Prüfe die Log-Datei (z. B. `src/blender_mcp/blender_mcp_server.log` bzw. `blender_mcp/blender_mcp_server.log` im Offline-Bundle). Wenn darin nur Startup-Meldungen stehen, aber keine `STDIN RAW LINE`-Einträge, sendet Kilo das `initialize`-Request nicht. Versuche dann den Batch-Wrapper-Workaround in Abschnitt 3.5.

### 3.5 Kilo-Workaround: Batch-Wrapper (Windows)

Falls Kilo Code den Server auf Windows nicht korrekt über `python.exe run.py` startet, kann ein kleiner Batch-Wrapper helfen, der Kilo als einzelnes Kommando übergeben wird:

Erstelle im Bundle-Ordner eine Datei `run_kilo.bat`:

```batch
@echo off
C:\Users\stefa\AppData\Local\Python\pythoncore-3.14-64\python.exe C:\Users\stefa\blender-mcp-slim\run.py
```

Passe die Pfade an deine Installation an. In `kilo.jsonc` verwende dann nur diesen einen Befehl:

```jsonc
{
  "mcp": {
    "blender": {
      "type": "local",
      "command": [
        "C:\\Users\\stefa\\blender-mcp-slim\\run_kilo.bat"
      ],
      "environment": {
        "PYTHONUNBUFFERED": "1",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "enabled": true,
      "timeout": 10000
    }
  }
}
```

Anschließend VSCodium neu starten.

---

## 4. Air-gapped / Offline-Betrieb

1. Kopiere den Ordner `offline/blender-mcp-slim/` auf den Zielrechner.
2. Stelle sicher, dass Python installiert ist (kein Internet, kein pip/uv nötig).
3. Verwende in der `mcp.json` absolute Pfade zur lokalen `python.exe` und zum lokalen `run.py`.
4. Optional: Setze `PYTHONUNBUFFERED=1` in der `env`-Sektion.

---

## 5. Manuelles Testen des Servers (ohne IDE)

Um zu prüfen, ob der Server korrekt startet und Nachrichten über stdout sendet, kannst du in PowerShell einen einfachen JSON-RPC-Handshake durchführen:

```powershell
$python = "C:\\Users\\stefa\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe"
$script = "C:\\Users\\stefa\\Sync\\code-agent\\mcp_slim_outback\\main.py"

$body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05"}}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes("Content-Length: $($body.Length)`r`n`r`n$body")

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $python
$psi.Arguments = $script
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$p = [System.Diagnostics.Process]::Start($psi)
$p.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
$p.StandardInput.BaseStream.Flush()
Start-Sleep -Milliseconds 500
$out = $p.StandardOutput.ReadToEnd()
$p.Kill()
Write-Output $out
```

Die Ausgabe sollte eine `Content-Length`-framed JSON-RPC-Antwort enthalten.

---

## 6. Bekannte Probleme und Hinweise

- **Windows + asyncio stdout:** Frühere Versionen des Servers verwendeten `asyncio.connect_write_pipe()` für stdout, was auf Windows mit `ProactorEventLoop` einen `NotImplementedError` auslöst. Die aktuelle Version schreibt stdout synchron, sodass der Server unter Windows stabil läuft.
- **Logging (stderr vs. Datei):** Damit MCP-Clients nur sauberes JSON-RPC auf stdout sehen, loggt der Server standardmäßig in eine Datei:  
  - Bei `main.py`: `<Repository>\src\blender_mcp\blender_mcp_server.log`  
  - Bei `offline/blender-mcp-slim/run.py`: `<Bundle>\blender_mcp\blender_mcp_server.log`  
  Um stattdessen nach stderr zu loggen (z. B. für Debugging), setze `BLENDER_MCP_LOG_STDERR=1` in der `env`-Sektion der Config.
- **Kilo Code 7.3.46: line-delimited JSON statt Content-Length framing:** Kilo Code sendet das MCP-Handshake nicht im Standard-Content-Length-Format, sondern als newline-delimited JSON. Der Server erkennt beide Formate automatisch und antwortet im gleichen Format, sodass Kilo Code, Cline/VS Code und andere Clients funktionieren.
- **Kilo Code: "Operation timed out after 10000ms":** Wenn der Server vor dem Handshake noch Logs nach stderr schreibt, kann Kilo Code das als Störung der stdout-Framing interpretieren. Die Log-Datei-Lösung oben behebt das in der Regel. Sollte der Fehler dennoch auftreten, prüfe die Log-Datei und/oder verwende den Batch-Wrapper in Abschnitt 3.5.
- **Blender-Verbindung:** Der Server versucht beim Start, eine TCP-Verbindung zu Blender herzustellen (`localhost:9876`). Falls Blender nicht läuft, wird nur eine Warnung geloggt; der Server bleibt aber aktiv und versucht bei jedem Tool-Aufruf erneut zu verbinden.

---

## 7. Zusammenfassung der Pfade

| Datei | Beschreibung |
|-------|--------------|
| `src/blender_mcp/mcp_minimal.py` | Quelle des MCP-stdio-Transports |
| `src/blender_mcp/server.py` | Quelle der Blender-Verbindung und Tool-Definitionen |
| `main.py` | Einstiegspunkt für Source-Checkout |
| `offline/blender-mcp-slim/run.py` | Einstiegspunkt für Offline-Betrieb |
| `scripts/build_offline_bundle.py` | Aktualisiert `offline/blender-mcp-slim/` nach Quelländerungen |
| `.vscode/mcp.json` | Workspace-Konfiguration für VS Code + Copilot |
| `cline_mcp_settings.json` | Beispiel-Config für Cline in VSCodium |
| `.kilo/kilo.jsonc` | Workspace-Konfiguration für Kilo Code in VSCodium |
| `~/.config/kilo/kilo.jsonc` | Globale User-Konfiguration für Kilo Code |
| `%APPDATA%\Code\User\mcp.json` | Globale User-Konfiguration für VS Code + Copilot |
| `blender_mcp/blender_mcp_server.log` | Server-Log-Datei (pro Instanz im Bundle/Source-Ordner) |

Passe alle Pfade an dein lokales System an, bevor du die Konfiguration verwendest.
