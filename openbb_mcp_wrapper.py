"""Windows-compatible wrapper for OpenBB MCP Server.

Fixes two Windows-specific issues:
1. cp950 encoding errors -> forces PYTHONUTF8=1
2. asyncio signal handlers not supported on Windows -> patches stdio_main
"""

import asyncio
import os
import sys

os.environ["PYTHONUTF8"] = "1"

import openbb_mcp_server.app.app as app_module


async def stdio_main_windows(mcp_server):
    """Run MCP server in STDIO mode without POSIX signal handlers."""
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, mcp_server.run, "stdio")


# Monkey-patch before main() is called
app_module.stdio_main = stdio_main_windows

if __name__ == "__main__":
    sys.argv = ["openbb-mcp", "--transport", "stdio"] + sys.argv[1:]
    app_module.main()
