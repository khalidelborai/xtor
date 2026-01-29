<!-- markdownlint-disable -->

# API Overview

## Modules

- [`cli`](./cli.md#module-cli): xtor CLI - Manage Tor instances.
- [`exceptions`](./exceptions.md#module-exceptions): Custom exceptions for xtor.
- [`pool`](./pool.md#module-pool): TorPool - Manage multiple Tor instances for high-throughput applications.
- [`state`](./state.md#module-state): State management for named Tor instances.
- [`tor`](./tor.md#module-tor)
- [`utils`](./utils.md#module-utils): Utility functions for xtor.

## Classes

- [`exceptions.AuthenticationError`](./exceptions.md#class-authenticationerror): Raised when authentication to Tor control port fails.
- [`exceptions.ConnectionError`](./exceptions.md#class-connectionerror): Raised when connection to Tor control port fails.
- [`exceptions.IdentityChangeTimeout`](./exceptions.md#class-identitychangetimeout): Raised when new identity request times out.
- [`exceptions.PortInUseError`](./exceptions.md#class-portinuseerror): Raised when the requested port is already in use.
- [`exceptions.TorNotFoundError`](./exceptions.md#class-tornotfounderror): Raised when tor binary cannot be found on system PATH.
- [`exceptions.XtorError`](./exceptions.md#class-xtorerror): Base exception for all xtor errors.
- [`pool.TorPool`](./pool.md#class-torpool): Pool of Tor instances for parallel requests with automatic port allocation.
- [`state.InstanceState`](./state.md#class-instancestate): State for a named Tor instance.
- [`tor.ExitNodeInfo`](./tor.md#class-exitnodeinfo): Information about the current Tor exit node.
- [`tor.HiddenService`](./tor.md#class-hiddenservice): Information about an ephemeral hidden service.
- [`tor.Tor`](./tor.md#class-tor): Tor instance for managing Tor connections and HTTP clients.

## Functions

- [`cli.check_process_running`](./cli.md#function-check_process_running): Check if a process with given PID is running.
- [`cli.connect`](./cli.md#function-connect): Show connection details for a named instance.
- [`cli.list_cmd`](./cli.md#function-list_cmd): List all managed Tor instances.
- [`cli.main`](./cli.md#function-main): CLI entry point.
- [`cli.remove`](./cli.md#function-remove): Stop and remove a named Tor instance completely.
- [`cli.start`](./cli.md#function-start): Start a named Tor instance.
- [`cli.stop`](./cli.md#function-stop): Stop a named Tor instance.
- [`state.get_instance`](./state.md#function-get_instance): Get a specific instance's state.
- [`state.get_instance_data_dir`](./state.md#function-get_instance_data_dir): Get or create the data directory for a named instance.
- [`state.get_instances_dir`](./state.md#function-get_instances_dir): Get the instances data directory, creating if needed.
- [`state.get_xtor_dir`](./state.md#function-get_xtor_dir): Get the xtor config directory, creating if needed.
- [`state.list_instances`](./state.md#function-list_instances): List all saved instances.
- [`state.read_state`](./state.md#function-read_state): Read all instance state from disk.
- [`state.remove_instance`](./state.md#function-remove_instance): Remove an instance from state. Returns True if found and removed.
- [`state.remove_instance_data_dir`](./state.md#function-remove_instance_data_dir): Remove the data directory for a named instance.
- [`state.save_instance`](./state.md#function-save_instance): Save an instance's state.
- [`state.write_state`](./state.md#function-write_state): Write instance state to disk with secure permissions.
- [`tor.generate_password`](./tor.md#function-generate_password): Generate a secure random password.
- [`utils.check_port_or_raise`](./utils.md#function-check_port_or_raise): Check if a port is available, raising an exception if not.
- [`utils.get_tor_pass_hash`](./utils.md#function-get_tor_pass_hash): Generate a hashed password for Tor control port authentication.
- [`utils.is_port_available`](./utils.md#function-is_port_available): Check if a port is available for binding.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
