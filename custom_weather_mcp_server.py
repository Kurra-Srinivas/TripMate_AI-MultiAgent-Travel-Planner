"""
Backward compatibility adapter for custom_weather_mcp_server.
Primary server module is now located in mcp_servers/custom_weather_mcp_server.py
"""
from mcp_servers.custom_weather_mcp_server import mcp, app, get_current_weather, get_forecast

if __name__ == "__main__":
    mcp.run(transport="stdio")