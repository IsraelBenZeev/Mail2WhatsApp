from agents import Agent, trace, Runner
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import asyncio
import os
# from urllib.parse import urlencode
# from mcp.client.streamable_http import streamablehttp_client
# from mcp import ClientSession

load_dotenv(override=True)

import pathlib

project_root = pathlib.Path(__file__).parent.parent

params = {
    "command": "uv",
    "args": ["run", "--directory", str(project_root), "python", "mcp_gmail.py"],
}


async def main():
    async with MCPServerStdio(
        params=params, client_session_timeout_seconds=30
    ) as server:
        mcp_tools = await server.session.list_tools()
        print(mcp_tools)


asyncio.run(main())
