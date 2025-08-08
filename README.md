xtor
===============================

xtor is a simple tool for managing Tor instances.

## Installation

- Linux
  - `sudo apt-get install tor`
  - `sudo apt-get install obfs4proxy`

- Windows
  - Download and install Tor Expert Bundle
    - `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-x86_64.tar.gz`
    - `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-i686.tar.gz`

Then install the python package:

`pip install xtor`

## CLI Usage

`xtor` now provides a command-line interface to manage multiple, named Tor instances.

### Start a new instance

To start a new instance named `my-instance`:

```bash
xtor start my-instance
```

This will start a Tor process in the background, with a randomly generated password. It will print the connection details upon creation. You can customize the ports, exit countries, and other options:

```bash
xtor start my-instance --port 9052 --control-port 9053 --countries US,GB
```

### List instances

You can list all your managed instances and see their status:

```bash
xtor list
```

### Stop an instance

To stop an instance:

```bash
xtor stop my-instance
```

### Remove an instance

This will stop the instance and remove its data directory:

```bash
xtor remove my-instance
```

### Get connection details

To see the connection details for an existing instance:

```bash
xtor connect my-instance
```

## Library Usage

The library can still be used to start and control Tor instances programmatically.

### Start an ephemeral instance

```python
from xtor import Tor

# Tor.create starts a new Tor process.
# By default, it's ephemeral and will be terminated when the script exits.
with Tor.create(port=9052, control_port=9053) as tor:
    print(f"Successfully connected to Tor with IP: {tor.ip}")
    response = tor.client.get("https://api.ipify.org")
    print(f"IP through Tor: {response.text}")
```

### Manage a persistent instance

You can also use the library to create and manage persistent, named instances, similar to the CLI.

```python
from xtor import Tor

# Create a named instance that will persist after the script exits
# Note: `own=False` is important for persistent instances
instance = Tor.create(name="my-persistent-instance", own=False)
print(f"Instance 'my-persistent-instance' started with PID: {instance.tor.pid}")

# Later, you can reconnect to it from another script
reconnected_instance = Tor.from_name("my-persistent-instance")
with reconnected_instance as tor:
    print(f"Reconnected to Tor with IP: {tor.ip}")

# And you can stop it when you're done
reconnected_instance.stop()
print("Instance stopped and state removed.")
```
