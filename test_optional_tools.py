#!/usr/bin/env python3
"""
Test script to verify that the MCP server gracefully handles missing tool configurations.
Tests that tools can be loaded optionally and that missing config doesn't crash the server.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Add the tools directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from tools import notion_tools, obsidian_tools, todoist_tools


class MockFastMCP:
    """A mock FastMCP class to intercept tool registrations."""

    def __init__(self):
        self.registered_tools = []

    def add_tool(self, func):
        """Record the registration of a tool function."""
        self.registered_tools.append(func.__name__)

    def tool(self, func):
        """Decorator version of tool registration."""
        self.add_tool(func)
        return func

    def clear(self):
        """Clear the list of registered tools."""
        self.registered_tools = []


class TestOptionalTools(unittest.TestCase):
    """
    Test suite for optional tool loading and runtime error handling.
    This test suite avoids running a subprocess and instead tests the registration
    and runtime logic of the tool modules directly.
    """

    def setUp(self):
        """Set up a clean environment for each test."""
        self.mock_mcp = MockFastMCP()
        self.temp_dir = tempfile.mkdtemp()

        # Backup original environment variables
        self.original_env = os.environ.copy()

        # Clear any potentially conflicting environment variables
        for key in ["NOTION_TOKEN", "TODOIST_TOKEN", "OBSIDIAN_VAULT_PATH", "NOTION_DATABASE_ID"]:
            if key in os.environ:
                del os.environ[key]
        
        # Reset lazy loading state in each module
        self.reset_tool_modules()

    def tearDown(self):
        """Restore the environment and clean up temporary files."""
        shutil.rmtree(self.temp_dir)
        os.environ.clear()
        os.environ.update(self.original_env)

    def reset_tool_modules(self):
        """
        Resets the internal state of tool modules to ensure test isolation.
        This is crucial because they use global variables for lazy loading.
        """
        # Notion
        notion_tools._env_loaded = False
        notion_tools._notion_token = None
        notion_tools._notion_client = None
        notion_tools._DEFAULT_DATABASE_ID = None

        # Todoist
        todoist_tools._env_loaded = False
        todoist_tools._todoist_token = None
        todoist_tools._api_client = None

        # Obsidian
        obsidian_tools._env_loaded = False
        obsidian_tools._OBSIDIAN_VAULT_PATH = None
        obsidian_tools._vault_path = None

    def test_no_config_no_tools_registered(self):
        """
        Verify that no tools are registered when no config is provided.
        """
        with patch('sys.stderr'): # Suppress stderr warnings
            notion_registered = notion_tools.register_tools(self.mock_mcp)
            todoist_registered = todoist_tools.register_tools(self.mock_mcp)
            obsidian_registered = obsidian_tools.register_tools(self.mock_mcp)

        self.assertFalse(notion_registered, "Notion should not be registered")
        self.assertFalse(todoist_registered, "Todoist should not be registered")
        self.assertFalse(obsidian_registered, "Obsidian should not be registered")
        self.assertEqual(len(self.mock_mcp.registered_tools), 0, "No tools should be in the MCP list")

    def test_partial_config_obsidian_only(self):
        """
        Verify that only Obsidian tools are registered when its config is present.
        """
        os.environ["OBSIDIAN_VAULT_PATH"] = self.temp_dir
        self.reset_tool_modules()

        with patch('sys.stderr'): # Suppress stderr warnings
            notion_registered = notion_tools.register_tools(self.mock_mcp)
            obsidian_registered = obsidian_tools.register_tools(self.mock_mcp)
            todoist_registered = todoist_tools.register_tools(self.mock_mcp)

        self.assertFalse(notion_registered, "Notion should not be registered")
        self.assertTrue(obsidian_registered, "Obsidian should be registered")
        self.assertFalse(todoist_registered, "Todoist should not be registered")
        
        self.assertIn("read_note", self.mock_mcp.registered_tools)
        self.assertNotIn("create_database_page", self.mock_mcp.registered_tools)
        self.assertNotIn("create_task", self.mock_mcp.registered_tools)

    def test_all_tools_configured(self):
        """
        Verify that all tools are registered when all configs are present.
        """
        os.environ["NOTION_TOKEN"] = "fake_notion_token"
        os.environ["TODOIST_TOKEN"] = "fake_todoist_token"
        os.environ["OBSIDIAN_VAULT_PATH"] = self.temp_dir
        self.reset_tool_modules()

        # Mock the client initializations to avoid actual API calls
        with patch('notion_client.Client'), patch('todoist_api_python.api.TodoistAPI'):
            notion_registered = notion_tools.register_tools(self.mock_mcp)
            todoist_registered = todoist_tools.register_tools(self.mock_mcp)
            obsidian_registered = obsidian_tools.register_tools(self.mock_mcp)

        self.assertTrue(notion_registered, "Notion should be registered")
        self.assertTrue(todoist_registered, "Todoist should be registered")
        self.assertTrue(obsidian_registered, "Obsidian should be registered")

        self.assertIn("create_database_page", self.mock_mcp.registered_tools)
        self.assertIn("create_task", self.mock_mcp.registered_tools)
        self.assertIn("create_note", self.mock_mcp.registered_tools)

    def test_runtime_errors_if_not_configured(self):
        """
        Verify that calling a tool function directly without configuration
        returns a clear error message.
        """
        # Test Notion
        result = notion_tools.create_database_page(title="Test")
        self.assertFalse(result["success"])
        self.assertIn("NOTION_TOKEN", result["error"])

        # Test Todoist
        result = todoist_tools.create_task(content="Test")
        self.assertFalse(result["success"])
        self.assertIn("TODOIST_TOKEN", result["error"])

        # Test Obsidian
        result = obsidian_tools.read_note(note_path="test.md")
        self.assertFalse(result["success"])
        self.assertIn("OBSIDIAN_VAULT_PATH", result["error"])

    def test_obsidian_requires_existing_path(self):
        """
        Verify that Obsidian tools do not register if the vault path does not exist.
        """
        os.environ["OBSIDIAN_VAULT_PATH"] = os.path.join(self.temp_dir, "non_existent_vault")
        self.reset_tool_modules()

        with patch('sys.stderr'): # Suppress stderr warnings
            obsidian_registered = obsidian_tools.register_tools(self.mock_mcp)

        self.assertFalse(obsidian_registered, "Obsidian should not register with a non-existent path")
        self.assertEqual(len(self.mock_mcp.registered_tools), 0)


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Optional Tool Loading (Resilient Mode)")
    print("=" * 60)
    
    # Create a TestLoader instance
    loader = unittest.TestLoader()
    
    # Load tests from the TestCase
    suite = loader.loadTestsFromTestCase(TestOptionalTools)
    
    # Create a TextTestRunner instance
    runner = unittest.TextTestRunner()
    
    # Run the test suite
    result = runner.run(suite)
    
    # Return exit code 0 if successful, 1 otherwise
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())