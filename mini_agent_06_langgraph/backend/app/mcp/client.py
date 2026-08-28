import json
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.core.config import TRAVEL_MCP_URL


@asynccontextmanager
async def travel_session():
    async with streamable_http_client(TRAVEL_MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def to_openai_tool(tool: Any) -> dict[str, Any]:
    raw = tool.model_dump(by_alias=True)
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": raw.get("inputSchema", {}),
    }


async def discover_tools() -> list[dict[str, Any]]:
    async with travel_session() as session:
        response = await session.list_tools()
        return [to_openai_tool(tool) for tool in response.tools]


async def call_tool(name: str, arguments: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    async with travel_session() as session:
        discovered = (await session.list_tools()).tools
        allowlist = {tool.name for tool in discovered}
        if name not in allowlist:
            raise ValueError(f"MCP Server가 제공하지 않는 Tool입니다: {name}")
        result = await session.call_tool(name, arguments=arguments)
        text = "\n".join(content.text for content in result.content if hasattr(content, "text"))
        if result.isError:
            raise RuntimeError(text or "MCP Tool 실행에 실패했습니다.")
        output = json.loads(text) if text else None
        return output, {
            "server": "travel",
            "transport": "streamable-http",
            "endpoint": TRAVEL_MCP_URL,
            "tool": name,
            "arguments": arguments,
            "result": output,
        }


async def connection_status() -> dict[str, Any]:
    tools = await discover_tools()
    return {
        "status": "connected",
        "server": "travel",
        "transport": "streamable-http",
        "endpoint": TRAVEL_MCP_URL,
        "tool_count": len(tools),
        "tools": [tool["name"] for tool in tools],
    }
