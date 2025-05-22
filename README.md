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
Most commands that interact with a Tor instance accept these options:
- `--host TEXT`: The host of the Tor SOCKS proxy/control port. Default: `127.0.0.1`.
- `--port INTEGER`: Port of the Tor SOCKS proxy. Default: `9052`.
- `--control-port INTEGER`: Port for Tor control. Default: `9053`.
- `--password TEXT`: Password for Tor control. Default: `password`.

### Commands

#### `xtor start`
Starts a new Tor server process. By default, it runs in the foreground, and you can stop it by pressing any key. When started this way, it also manages a PID file.

```bash
# Start a Tor server with default settings (SOCKS on 9052, Control on 9053)
xtor start

# Start Tor on different ports
xtor start --port 9060 --control-port 9061

# Start Tor specifying a path to the Tor binary and allowed exit countries
xtor start --path /usr/sbin/tor --countries US,GB
```
When `xtor start` is run with `own=True` (the default for the CLI), it creates a PID file at `~/.cache/xtor/{control_port}.pid`. If you stop the interactive session (e.g., by pressing a key or Ctrl+C), `xtor` will stop the Tor process and remove this PID file.

#### `xtor status`
Connects to an existing Tor instance and prints its current external IP address.

```bash
# Get status for Tor instance with default control port 9053
xtor status

# Get status for Tor instance on a different control port
xtor status --control-port 9055
```

#### `xtor new-identity`
Requests a new IP address (new identity) from an existing Tor instance.

```bash
# Request a new identity for Tor on default control port 9053
xtor new-identity

# Request and wait for the new IP to be confirmed
xtor new-identity --wait

# Request new identity for Tor on a different control port
xtor new-identity --control-port 9055 --password mysecretpassword
```

#### `xtor stop`
Stops an `xtor`-managed Tor process. It finds the process by reading the PID from the PID file created by `xtor start`.

```bash
# Stop the Tor instance that was started with control port 9053 (default)
xtor stop

# Stop a Tor instance associated with a different control port
xtor stop --control-port 9061
```

### PID File Management
`xtor` uses PID (Process ID) files to keep track of the Tor processes it starts.
- **Location**: `~/.cache/xtor/{control_port}.pid` (e.g., `~/.cache/xtor/9053.pid`).
- **Purpose**:
    - The `xtor start` command (when run interactively) writes the Tor process's PID to this file.
    - The `xtor stop --control-port <port>` command reads the PID from the corresponding file to know which process to terminate.
- **Automatic Cleanup**:
    - If you stop an interactively run `xtor start` session (e.g., by pressing a key), the PID file is automatically removed.
    - The `xtor stop` command removes the PID file after successfully stopping the Tor process.

This system allows `xtor` to manage its own Tor processes effectively. If you manually kill a Tor process started by `xtor start`, you may need to remove the corresponding PID file manually.
