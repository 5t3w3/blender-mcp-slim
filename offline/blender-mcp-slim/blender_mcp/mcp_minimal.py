"""Minimal self-contained implementation of the Model Context Protocol.

This module provides the tiny subset of MCP used by blender-mcp-slim:
- stdio JSON-RPC transport with Content-Length framing
- initialize / notifications/initialized / tools/list / tools/call
- @tool() decorator with JSON schema generation from type hints
- Context injection and Image return values

It intentionally does not implement prompts, resources, sampling, roots,
or any transport other than stdio.
"""

from __future__ import annotations

import asyncio
import base64
import inspect
import json
import logging
import sys
import threading
import traceback
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Type, Union, get_type_hints

logger = logging.getLogger("mcp_minimal")


# ---------------------------------------------------------------------------
# Public data types
# ---------------------------------------------------------------------------


class Context:
    """No-op Context stub; the current tools declare it but do not use it."""

    def __init__(self) -> None:
        pass


@dataclass
class Image:
    """Represents an image returned by a tool."""

    data: bytes
    format: str = "png"

    @property
    def mime_type(self) -> str:
        return f"image/{self.format}"

    def to_content(self) -> Dict[str, str]:
        return {
            "type": "image",
            "data": base64.b64encode(self.data).decode("ascii"),
            "mimeType": self.mime_type,
        }


# ---------------------------------------------------------------------------
# JSON schema generation for tool parameters
# ---------------------------------------------------------------------------


_JSON_SCHEMA_TYPES: Dict[Type[Any], str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
}


def _is_optional(param: inspect.Parameter) -> bool:
    return param.default is not inspect.Parameter.empty


def _param_description(docstring: Optional[str], param_name: str) -> Optional[str]:
    """Extract a parameter description from a Google/NumPy-ish docstring."""
    if not docstring:
        return None
    lines = docstring.strip().splitlines()
    in_section = False
    descriptions: List[str] = []
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        if lower in {"parameters:", "args:", "arguments:", "params:"}:
            in_section = True
            continue
        if in_section:
            if stripped == "":
                continue
            if stripped.endswith(":") and not stripped.startswith("-"):
                # Looks like a new section header
                break
            if stripped.startswith("-") or stripped.startswith("*"):
                stripped = stripped[1:].strip()
            # Match "name: description" or "name (type): description"
            if ":" in stripped:
                name_part, desc = stripped.split(":", 1)
                name_part = name_part.strip()
                # Strip type annotations like "object_name (str)"
                if "(" in name_part and name_part.endswith(")"):
                    name_part = name_part.split("(", 1)[0].strip()
                if name_part == param_name:
                    descriptions.append(desc.strip())
            elif stripped.startswith(param_name + " ") or stripped == param_name:
                # Parameter name on its own line, description on next line(s)
                descriptions.append("")
    if descriptions:
        return " ".join(d for d in descriptions if d).strip() or None
    return None


def _make_input_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    """Build a JSON Schema 'inputSchema' object for *func*."""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    properties: Dict[str, Any] = {}
    required: List[str] = []

    for name, param in sig.parameters.items():
        if _is_context_param(name, param):
            continue
        py_type = type_hints.get(name, str)
        schema_type = _JSON_SCHEMA_TYPES.get(py_type, "string")
        prop: Dict[str, Any] = {"type": schema_type}
        description = _param_description(func.__doc__, name)
        if description:
            prop["description"] = description
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def _is_context_param(name: str, param: inspect.Parameter) -> bool:
    """Return True if a parameter should be injected as a Context."""
    annotation = param.annotation
    if annotation is inspect.Parameter.empty:
        return False
    # Handle string annotations or forward references
    if isinstance(annotation, str):
        return annotation in {"Context", "mcp_minimal.Context", "blender_mcp.mcp_minimal.Context"}
    try:
        return annotation is Context or (
            hasattr(annotation, "__origin__") is False
            and isinstance(annotation, type)
            and annotation.__name__ == "Context"
        )
    except Exception:
        return False


def _tool_description(func: Callable[..., Any]) -> str:
    """Return the function's docstring summary, if any."""
    if not func.__doc__:
        return ""
    return func.__doc__.strip().splitlines()[0].strip()


# ---------------------------------------------------------------------------
# Tool registration and FastMCP server
# ---------------------------------------------------------------------------


@dataclass
class _RegisteredTool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    func: Callable[..., Any]


class FastMCP:
    """Minimal MCP server implementing exactly what blender-mcp-slim needs."""

    def __init__(self, name: str, lifespan: Optional[Callable[["FastMCP"], AbstractAsyncContextManager[Any]]] = None) -> None:
        self.name = name
        self.lifespan = lifespan
        self._tools: Dict[str, _RegisteredTool] = {}

    def tool(self, name: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator that registers a function as an MCP tool."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            tool_name = name or func.__name__
            self._tools[tool_name] = _RegisteredTool(
                name=tool_name,
                description=_tool_description(func),
                input_schema=_make_input_schema(func),
                func=func,
            )
            return func
        return decorator

    def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        client_version = params.get("protocolVersion", "2024-11-05")
        logger.info(f"Client initialized with protocol {client_version}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": client_version,
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": self.name,
                    "version": "1.5.5",
                },
            },
        }

    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.input_schema,
                    }
                    for t in self._tools.values()
                ],
            },
        }

    async def _handle_tool_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        tool = self._tools.get(tool_name)
        if tool is None:
            return self._error_response(request_id, -32602, f"Tool not found: {tool_name}")

        try:
            result = await self._invoke_tool(tool, arguments)
        except Exception as exc:
            logger.error(f"Tool {tool_name} raised an exception: {exc}")
            logger.debug(traceback.format_exc())
            return self._error_response(
                request_id,
                -32603,
                f"Tool execution failed: {exc}",
                data={"traceback": traceback.format_exc()},
            )

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    async def _invoke_tool(self, tool: _RegisteredTool, arguments: Dict[str, Any]) -> Dict[str, Any]:
        sig = inspect.signature(tool.func)
        kwargs: Dict[str, Any] = {}
        for name, param in sig.parameters.items():
            if _is_context_param(name, param):
                kwargs[name] = Context()
            elif name in arguments:
                kwargs[name] = arguments[name]
            elif param.default is not inspect.Parameter.empty:
                kwargs[name] = param.default
            else:
                raise TypeError(f"Missing required argument: {name}")

        if inspect.iscoroutinefunction(tool.func):
            raw_result = await tool.func(**kwargs)
        else:
            raw_result = tool.func(**kwargs)

        if isinstance(raw_result, Image):
            return {
                "content": [raw_result.to_content()],
                "isError": False,
            }
        return {
            "content": [{"type": "text", "text": str(raw_result)}],
            "isError": False,
        }

    def _error_response(self, request_id: Any, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        error: Dict[str, Any] = {"code": code, "message": message}
        if data:
            error["data"] = data
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error,
        }

    async def _handle_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")

        if method == "initialize":
            return self._handle_initialize(request_id, params)
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return self._handle_tools_list(request_id)
        if method == "tools/call":
            return await self._handle_tool_call(request_id, params)

        return self._error_response(request_id, -32601, f"Method not found: {method}")

    async def _run_loop(self) -> None:
        """Read JSON-RPC messages from stdin and write responses to stdout.

        stdin is read from a dedicated thread so the server also works on
        Windows when stdin is a console handle instead of a pipe. stdout is
        written synchronously because asyncio pipe writes are not supported on
        Windows by the default ProactorEventLoop.
        """
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(line_buffering=True)

        loop = asyncio.get_running_loop()
        message_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        shutdown_event = threading.Event()

        reader_thread = threading.Thread(
            target=_sync_stdin_reader,
            args=(loop, message_queue, shutdown_event),
            daemon=True,
        )
        reader_thread.start()

        try:
            while True:
                try:
                    message = await asyncio.wait_for(message_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    if shutdown_event.is_set():
                        break
                    continue

                response = await self._handle_request(message)
                if response is not None:
                    _write_message_sync(response)
        finally:
            shutdown_event.set()
            reader_thread.join(timeout=1.0)

    def run(self) -> None:
        """Run the stdio MCP server."""
        if self.lifespan is None:
            asyncio.run(self._run_loop())
            return

        async def _run_with_lifespan() -> None:
            async with self.lifespan(self):
                await self._run_loop()

        asyncio.run(_run_with_lifespan())


# ---------------------------------------------------------------------------
# Content-Length framed stdio helpers
# ---------------------------------------------------------------------------

# Kilo Code 7.3.46 sends line-delimited JSON instead of the standard
# Content-Length framed JSON-RPC. We detect the format from the first request
# and respond in the same format.
_transport_format = "content-length"


def _set_transport_format(fmt: str) -> None:
    global _transport_format
    if _transport_format != fmt:
        logger.info(f"Switching transport format to {fmt}")
        _transport_format = fmt


def _sync_stdin_reader(
    loop: asyncio.AbstractEventLoop,
    queue: asyncio.Queue[Dict[str, Any]],
    shutdown_event: threading.Event,
) -> None:
    """Synchronous stdin reader running in its own thread."""
    stdin = sys.stdin.buffer
    try:
        while not shutdown_event.is_set():
            line = stdin.readline()
            if not line:
                return

            line_str = line.decode("utf-8", errors="replace").strip()
            if line_str == "":
                continue

            if line_str.lower().startswith("content-length:"):
                _set_transport_format("content-length")
                try:
                    content_length = int(line_str.split(":", 1)[1].strip())
                except ValueError:
                    continue

                # Read the blank line separator.
                stdin.readline()

                body = stdin.read(content_length)
                if len(body) < content_length:
                    return

                try:
                    message = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError as exc:
                    logger.error(f"Failed to decode JSON-RPC body: {exc}")
                    continue
            else:
                _set_transport_format("line-delimited")
                try:
                    message = json.loads(line_str)
                except json.JSONDecodeError as exc:
                    logger.error(f"Failed to decode line-delimited JSON: {exc}")
                    continue

            asyncio.run_coroutine_threadsafe(queue.put(message), loop)
    except Exception as exc:
        logger.error(f"stdin reader thread error: {exc}")


def _write_message_sync(message: Dict[str, Any]) -> None:
    """Write a JSON-RPC message to stdout using the detected transport format."""
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    if _transport_format == "line-delimited":
        payload = body + b"\n"
    else:
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        payload = header + body
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()
