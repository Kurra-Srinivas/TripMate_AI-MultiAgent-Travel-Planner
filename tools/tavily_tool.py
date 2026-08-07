import asyncio
from typing import Any
from mcp_client import tavily_mcp_search


async def search_web_info_async(query: str) -> Any:
    """Perform async web search using Tavily MCP."""
    return await tavily_mcp_search(query)


def search_web_info(query: str) -> Any:
    """Synchronous wrapper to execute Tavily search."""
    try:
        return asyncio.run(search_web_info_async(query))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(search_web_info_async(query))


# Alias for tavily_search to maintain backwards compatibility across tests and custom scripts
tavily_search = search_web_info
