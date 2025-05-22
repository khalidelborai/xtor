xtor
===============================

xtor is a simple tool for managing Tor instances.

## Installation

- Linux
  - `sudo apt-get install tor`
  - `sudo apt-get install obfs4proxy` (optional, typically only needed when using Tor bridges for censorship circumvention)

- Windows
  - Download and install the Tor Expert Bundle from the official Tor Project website.
    - For example: `https://www.torproject.org/download/tor/` (Choose the "Expert Bundle")

Then install the python package:

`pip install xtor`

## Usage

```python
from xtor import Tor

tor = Tor.startTor(
    port=9052,
    control_port=9053,
    host="127.0.0.1",
    password="passw0rd",
    init_msg_handler=print,
    path="/usr/bin/tor", # optional, primarily for windows
)

with tor:
  print(tor.ip)
  print(tor.client.get("https://api.ipify.org").text)


# connect to an existing tor instance

tor = Tor(
    port=9052,
    control_port=9053,
    host="127.0.0.1",
    password="passw0rd",
)

with tor:
  print(tor.ip)
  print(tor.client.get("https://api.ipify.org").text)
  tor.new_identity(wait=True) # get a new identity and wait for it to be ready (new ip)
  print(tor.ip)
```

## CLI

The `xtor` command-line interface allows you to manage Tor instances. You can get help for any command by using the `--help` flag, for example, `xtor start --help`.

### Common Options
Most commands that interact with a Tor instance accept these options for direct control or as overrides for instance configurations:
- `--host TEXT`: The host of the Tor SOCKS proxy/control port. Default: `127.0.0.1`.
- `--port INTEGER`: Port of the Tor SOCKS proxy. Default: `9052`.
- `--control-port INTEGER`: Port for Tor control. Default: `9053`.
- `--password TEXT`: Password for Tor control. Default: `password`.
- `--path TEXT`: Path to the Tor binary. Default: `tor`.
- `--countries TEXT`: Comma-separated list of exit node countries. Default: (none).
- `--max-time INTEGER`: Max circuit dirtiness in seconds (0 for none). Default: `0`.
- `--own / --no-own`: Whether xtor should take ownership of the Tor process. Default: `True`.


### Instance Configuration Management

`xtor` allows you to save and manage multiple named Tor configurations. This is useful if you frequently use different Tor setups. Configurations are stored in `~/.config/xtor/instances.json`.

All instance management commands are subcommands of `xtor instance`:

#### `xtor instance create`
Creates and saves a new named Tor instance configuration.

**Syntax:**
`xtor instance create --id <instance_id> [OPTIONS]`

**Options (besides common options listed above):**
- `--id TEXT`: (Required) Unique identifier for the new instance configuration.

**Example:**
```bash
# Create a configuration for a "dev" instance
xtor instance create --id dev --port 9050 --control-port 9051 --countries US,CA --max-time 3600

# Create a configuration for a "secure" instance with a specific path
xtor instance create --id secure --path /opt/tor/bin/tor --password securepass
```

#### `xtor instance list`
Lists all saved Tor instance configurations.

**Syntax:**
`xtor instance list`

**Example:**
```bash
xtor instance list
```
**Output Example:**
```
Available instance configurations:

Instance ID: dev
{
  "port": 9050,
  "host": "127.0.0.1",
  "control_port": 9051,
  "password": "password",
  "path": "tor",
  "countries": [
    "US",
    "CA"
  ],
  "max_circuit_dirtiness": 3600,
  "own": true,
  "client_options": {},
  "torrc_config": {}
}

Instance ID: secure
{
  "port": 9052,
  "host": "127.0.0.1",
  "control_port": 9053,
  "password": "securepass",
  "path": "/opt/tor/bin/tor",
  "countries": [],
  "max_circuit_dirtiness": 0,
  "own": true,
  "client_options": {},
  "torrc_config": {}
}
```

#### `xtor instance delete`
Deletes a saved Tor instance configuration.

**Syntax:**
`xtor instance delete --id <instance_id>`

**Example:**
```bash
xtor instance delete --id dev
```

#### `xtor instance update`
Updates an existing Tor instance configuration. Only the provided fields are changed.

**Syntax:**
`xtor instance update --id <instance_id> [OPTIONS]`

**Example:**
```bash
# Update the port for the "secure" instance
xtor instance update --id secure --port 9055

# Clear the countries list for the "dev" instance
xtor instance update --id dev --countries ""
```

### Direct Commands (and using Instance Configurations)

These commands can operate either with directly provided parameters or by using a saved instance configuration via the `--instance-id` option.

#### `xtor start`
Starts a new Tor server process.

**Options:**
- `--instance-id TEXT`: (Optional) Start Tor using a saved instance configuration ID.
- All common options listed above can be used to override values from an instance configuration or for direct startup.

```bash
# Start a Tor server with default settings (SOCKS on 9052, Control on 9053)
xtor start

# Start Tor on different ports
xtor start --port 9060 --control-port 9061

# Start Tor specifying a path to the Tor binary and allowed exit countries
xtor start --path /usr/sbin/tor --countries US,GB
```
When `xtor start` is run with `own=True` (either from instance config or default/override), it creates a PID file. If you stop the interactive session (e.g., by pressing a key or Ctrl+C), `xtor` will stop the Tor process and remove this PID file. See "PID File Management" for details on naming.

**Examples:**
```bash
# Start a Tor server using direct parameters (SOCKS on 9052, Control on 9053)
xtor start

# Start Tor using a saved instance configuration "dev"
xtor start --instance-id dev

# Start Tor using instance "dev" but override the port
xtor start --instance-id dev --port 9999
```

#### `xtor status`
Connects to an existing Tor instance and prints its current external IP address.

**Options:**
- `--instance-id TEXT`: (Optional) Use connection parameters from a saved instance configuration ID.
- Common options (`--host`, `--port`, `--control-port`, `--password`) can be used to override or specify directly.

```bash
# Get status for Tor instance with default direct parameters
xtor status

# Get status using saved instance "dev"
xtor status --instance-id dev

# Get status using instance "dev" but override control port
xtor status --instance-id dev --control-port 9055
```

#### `xtor new-identity`
Requests a new IP address (new identity) from an existing Tor instance.

**Options:**
- `--instance-id TEXT`: (Optional) Use connection parameters from a saved instance configuration ID.
- Common options (`--host`, `--port`, `--control-port`, `--password`) can be used to override or specify directly.
- `--wait / --no-wait`: Wait for the new identity to be confirmed with a new IP. Default: `False`.

```bash
# Request new identity using default direct parameters
xtor new-identity

# Request new identity using saved instance "dev" and wait
xtor new-identity --instance-id dev --wait
```

#### `xtor stop`
Stops an `xtor`-managed Tor process. It finds the process by reading its PID from a PID file.

**Options:**
- `--instance-id TEXT`: (Optional) Stop the Tor instance associated with this configuration ID (targets `<instance_id>.pid`).
- `--control-port INTEGER`: (Optional) Control port of the Tor instance to stop (targets `<control_port>.pid`). Used if `--instance-id` is not provided.
> Note: `--instance-id` and `--control-port` are mutually exclusive for identifying the process to stop.

```bash
# Stop the Tor instance associated with instance ID "dev"
xtor stop --instance-id dev

# Stop a Tor instance by its control port (if not started with an instance ID)
xtor stop --control-port 9053
```

### PID File Management
`xtor` uses PID (Process ID) files to keep track of the Tor processes it starts when the `own` flag is active (default for `xtor start`).

- **Location**: `~/.cache/xtor/`
- **Naming Convention**:
    - If `xtor start` is used with `--instance-id <name>`, the PID file is named `<name>.pid` (e.g., `dev.pid`).
    - If `xtor start` is used without `--instance-id`, the PID file is named after the effective control port: `<control_port_value>.pid` (e.g., `9053.pid`).
- **Purpose**:
    - The `xtor start` command writes the Tor process's PID to the appropriately named file.
    - The `xtor stop` command uses either `--instance-id <name>` or `--control-port <port>` to find the corresponding PID file and terminate the process.
- **Automatic Cleanup**:
    - If you stop an interactively run `xtor start` session (e.g., by pressing a key or Ctrl+C), the corresponding PID file is automatically removed.
    - The `xtor stop` command removes the PID file after successfully stopping the Tor process.

This system allows `xtor` to manage its own Tor processes effectively. If you manually kill a Tor process started by `xtor start`, you may need to remove the corresponding PID file manually from `~/.cache/xtor/`.
