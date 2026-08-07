import sys
from pathlib import Path

# Ensure project root directory is in sys.path when running script directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp_client import client, WEATHER_SERVER_PATH


class TestMCPClient(unittest.TestCase):
    def test_weather_server_path_exists(self):
        """Verify that custom weather MCP server script exists at expected location."""
        self.assertTrue(WEATHER_SERVER_PATH.exists())
        self.assertEqual(WEATHER_SERVER_PATH.name, "custom_weather_mcp_server.py")
        self.assertEqual(WEATHER_SERVER_PATH.parent.name, "mcp_servers")

    def test_mcp_client_instance(self):
        """Verify that client is an instance of MultiServerMCPClient."""
        self.assertIsInstance(client, MultiServerMCPClient)
        self.assertTrue(hasattr(client, "get_tools"))

    def test_weather_mcp_server_import(self):
        """Verify weather MCP server app can be imported directly."""
        from mcp_servers.custom_weather_mcp_server import app as weather_app
        self.assertIsNotNone(weather_app)


if __name__ == "__main__":
    unittest.main()
