# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xtor is a Python library for managing Tor instances programmatically. It wraps the `stem` library for Tor control and provides an `httpx` client pre-configured with SOCKS5 proxy support.

## Requirements

- Python 3.10+
- Tor installed on system PATH (or specify path explicitly)

## Build & Development Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run xtor --help
uv run xtor start my-tor --port 9052 --control-port 9053 --password mypass
uv run xtor list
uv run xtor connect my-tor
uv run xtor stop my-tor
uv run xtor remove my-tor

# Generate API documentation (outputs to docs/)
uv run lazydocs --overview-file README.md xtor
```

## Architecture

The library consists of six modules:

- **xtor/tor.py** - Core `Tor` class with two usage patterns:
  - `Tor.start(...)` - Launch a new Tor process via `stem.process.launch_tor_with_config`
  - `Tor(...)` constructor - Connect to an existing Tor instance
  - `Tor.from_name(...)` - Reconnect to a named instance
  - Both use context manager (`with tor:`) for controller authentication lifecycle
  - `.client` / `.async_client` properties return pre-configured httpx clients with SOCKS5 proxy
  - `.isolated_client(key)` / `.isolated_async_client(key)` for stream isolation
  - Circuit management: `get_circuits()`, `close_circuit()`, `get_streams()`, `attach_stream()`
  - Exit node info: `get_exit_node_info()`, `.exit_node` property
  - Hidden services: `create_hidden_service()`, `remove_hidden_service()`, `list_hidden_services()`
  - Event listeners: `add_event_listener()`, `remove_event_listener()`
  - Status properties: `.version`, `.uptime`, `.is_alive`, `.can_new_identity`, `.newnym_wait`
  - Note: `Tor.startTor()` is kept as an alias for backwards compatibility

- **xtor/pool.py** - `TorPool` class for managing multiple Tor instances:
  - Automatic port allocation from a base port
  - Round-robin (`next()`), random (`random()`), and index-based (`get()`) selection
  - Bulk identity rotation (`rotate_all()`) and single rotation (`rotate_one()`)
  - Context manager support

- **xtor/state.py** - State management for named instances:
  - `InstanceState` dataclass with name, pid, ports, password, host, data_dir
  - Persistent state in `~/.xtor/state.json` with secure permissions
  - Functions: `save_instance()`, `get_instance()`, `remove_instance()`, `list_instances()`

- **xtor/exceptions.py** - Custom exception hierarchy:
  - `XtorError` - Base exception for all xtor errors
  - `TorNotFoundError` - Tor binary not found on PATH
  - `PortInUseError` - Requested port already in use
  - `IdentityChangeTimeout` - New identity request timed out
  - `ConnectionError` - Control port connection failed
  - `AuthenticationError` - Control port authentication failed

- **xtor/utils.py** - Utility functions (snake_case API):
  - `get_tor_pass_hash()` - Generates Tor-compatible hashed password
  - `is_port_available()` - Checks if a port is free
  - `check_port_or_raise()` - Validates port availability, raises on failure

- **xtor/cli.py** - Typer-based CLI with five commands:
  - `start` - Start a named Tor instance
  - `stop` - Stop a named instance
  - `remove` - Stop and remove instance with data
  - `list` - List all managed instances
  - `connect` - Show connection details for an instance

## Key Dependencies

- `stem` - Official Tor controller library
- `httpx[socks]` - HTTP client with SOCKS5 proxy support
- `where` - Finds tor binary on system PATH
- `typer` - CLI framework
