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
uv run xtor start --port 9052 --control-port 9053 --password mypass

# Generate API documentation (outputs to docs/)
uv run lazydocs --overview-file README.md xtor
```

## Architecture

The library consists of four modules:

- **xtor/tor.py** - Core `Tor` class with two usage patterns:
  - `Tor.start(...)` - Launch a new Tor process via `stem.process.launch_tor_with_config`
  - `Tor(...)` constructor - Connect to an existing Tor instance
  - Both use context manager (`with tor:`) for controller authentication lifecycle
  - `.client` property returns a pre-configured `httpx.Client` with SOCKS5 proxy
  - Note: `Tor.startTor()` is kept as an alias for backwards compatibility

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

- **xtor/cli.py** - Typer-based CLI that exposes `start` command

## Key Dependencies

- `stem` - Official Tor controller library
- `httpx[socks]` - HTTP client with SOCKS5 proxy support
- `where` - Finds tor binary on system PATH
- `typer` - CLI framework
