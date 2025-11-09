#!/usr/bin/env python3
"""
Test script to verify that the MCP server gracefully handles missing tool configurations.
Tests that tools can be loaded optionally and that missing config doesn't crash the server.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_server_with_env(env_vars, timeout=3):
    """
    Run the server with specific environment variables and capture output.

    Args:
        env_vars: Dict of environment variables to set
        timeout: Seconds to run before terminating

    Returns:
        Tuple of (stdout, stderr, return_code)
    """
    env = os.environ.copy()
    env.update(env_vars)

    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as e:
        return e.stdout or "", e.stderr or "", 0
    except Exception as e:
        return "", str(e), 1


def test_no_config():
    """Test server starts with no configuration - no tools should load."""
    print("Test 1: No configuration")
    print("-" * 60)

    # Ensure no tool env vars are set
    env_vars = {
        "NOTION_TOKEN": "",
        "TODOIST_TOKEN": "",
        "OBSIDIAN_VAULT_PATH": "",
    }

    stdout, stderr, code = run_server_with_env(env_vars)

    # Check that warnings are shown
    assert "⚠ Notion tools not registered" in stderr, "Should warn about Notion"
    assert "⚠ Todoist tools not registered" in stderr, "Should warn about Todoist"
    assert "⚠ Obsidian tools not registered" in stderr, "Should warn about Obsidian"
    assert "⚠ Warning: No tools loaded" in stderr, "Should show no tools warning"

    print("✓ Server starts gracefully with no config")
    print("✓ All tools show appropriate warnings")
    print()


def test_partial_config():
    """Test server with only one tool configured."""
    print("Test 2: Partial configuration (Obsidian only)")
    print("-" * 60)

    # Create a temporary directory for Obsidian vault to test path validation
    with tempfile.TemporaryDirectory() as temp_dir:
        env_vars = {
            "NOTION_TOKEN": "",  # Not set
            "TODOIST_TOKEN": "",  # Not set
            "OBSIDIAN_VAULT_PATH": temp_dir,  # Valid path
        }

        stdout, stderr, code = run_server_with_env(env_vars)

        # Obsidian should load, others should warn
        assert "✓ Obsidian tools: LOADED" in stderr, "Obsidian should load"
        assert "⚠ Notion tools not registered" in stderr, "Should warn about Notion"
        assert "⚠ Todoist tools not registered" in stderr, "Should warn about Todoist"

        print("✓ Server handles partial configuration")
        print()


def test_tool_error_messages():
    """Test that tools return proper error messages when called without config."""
    print("Test 3: Tool error messages")
    print("-" * 60)

    # This test would require actually calling the tools via MCP protocol
    # For now, we'll verify the error handling logic is in place
    # by checking that the config check functions exist

    from tools import notion_tools, todoist_tools, obsidian_tools

    # Test Notion config check
    is_configured, error = notion_tools._check_config()
    assert not is_configured, "Notion should not be configured"
    assert "NOTION_TOKEN" in error, "Error should mention NOTION_TOKEN"

    # Test Todoist config check
    is_configured, error = todoist_tools._check_config()
    assert not is_configured, "Todoist should not be configured"
    assert "TODOIST_TOKEN" in error, "Error should mention TODOIST_TOKEN"

    # Test Obsidian config check
    is_configured, error = obsidian_tools._check_config()
    assert not is_configured, "Obsidian should not be configured"
    assert "OBSIDIAN_VAULT_PATH" in error, "Error should mention OBSIDIAN_VAULT_PATH"

    print("✓ All tools have proper config validation")
    print()


def test_with_valid_obsidian():
    """Test with a valid Obsidian vault path."""
    print("Test 4: Valid Obsidian configuration")
    print("-" * 60)

    with tempfile.TemporaryDirectory() as temp_vault:
        env_vars = {
            "NOTION_TOKEN": "",
            "TODOIST_TOKEN": "",
            "OBSIDIAN_VAULT_PATH": temp_vault,
        }

        stdout, stderr, code = run_server_with_env(env_vars)

        # Obsidian should load successfully
        assert "✓ Obsidian tools: LOADED" in stderr, "Obsidian should load"
        assert "⚠ Notion tools not registered" in stderr, "Notion should warn"
        assert "⚠ Todoist tools not registered" in stderr, "Todoist should warn"

        print("✓ Obsidian loads with valid vault path")
        print()


def test_all_tools_configured():
    """Test with all tools configured."""
    print("Test 5: All tools configured")
    print("-" * 60)

    with tempfile.TemporaryDirectory() as temp_vault:
        env_vars = {
            "NOTION_TOKEN": "fake_notion_token",
            "TODOIST_TOKEN": "fake_todoist_token",
            "OBSIDIAN_VAULT_PATH": temp_vault,
            "NOTION_DATABASE_ID": "fake_db_id",
        }

        stdout, stderr, code = run_server_with_env(env_vars)

        # All tools should attempt to load
        assert "Notion tools" in stderr, "Should mention Notion"
        assert "Todoist tools" in stderr, "Should mention Todoist"
        assert "✓ Obsidian tools: LOADED" in stderr, "Obsidian should load"

        print("✓ All tools attempt to load when configured")
        print()


def test_runtime_tool_calls():
    """Test that tools return proper errors when called without config."""
    print("Test 6: Runtime tool call error handling")
    print("-" * 60)

    # Import tools
    from tools import notion_tools, todoist_tools, obsidian_tools

    # Test Notion tool without config
    result = notion_tools.create_database_page(title="Test Page", database_id="test_db")
    assert not result["success"], "Should fail without config"
    assert "NOTION_TOKEN" in result["error"], "Error should mention token"

    # Test Todoist tool without config
    result = todoist_tools.create_task(content="Test task")
    assert not result["success"], "Should fail without config"
    assert "TODOIST_TOKEN" in result["error"], "Error should mention token"

    # Test Obsidian tool without config
    result = obsidian_tools.read_note(note_path="test.md")
    assert not result["success"], "Should fail without config"
    assert "OBSIDIAN_VAULT_PATH" in result["error"], "Error should mention vault path"

    print("✓ Tools return proper errors at runtime")
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Optional Tool Loading")
    print("=" * 60)
    print()

    # Change to the correct directory
    os.chdir(Path(__file__).parent)

    try:
        test_no_config()
        test_partial_config()
        test_tool_error_messages()
        test_with_valid_obsidian()
        test_all_tools_configured()
        test_runtime_tool_calls()

        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
