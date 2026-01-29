# xtor

Python library for managing Tor instances programmatically.

[![PyPI version](https://img.shields.io/pypi/v/xtor)](https://pypi.org/project/xtor/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/license-GPL--3.0--or--later-green)](https://www.gnu.org/licenses/gpl-3.0.html)
[![CI](https://github.com/khalidelborai/xtor/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/khalidelborai/xtor/actions/workflows/test.yml)

## Features

- Launch new Tor processes or connect to existing ones
- Pre-configured httpx clients (sync + async) with SOCKS5 proxy
- Identity rotation with optional wait-for-new-IP
- Stream isolation for traffic separation
- Circuit and stream management
- Exit node info (country, bandwidth, flags)
- Ephemeral hidden services (.onion)
- Event listeners (circuit, stream, bandwidth events)
- TorPool for managing multiple instances with round-robin and random selection
- Named instances with CLI management
- Custom exception hierarchy for precise error handling

## Installation

### Prerequisites

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get install tor obfs4proxy
```

**Windows:**

Download the Tor Expert Bundle from [torproject.org](https://www.torproject.org/download/tor/).

### Python Package

```bash
pip install xtor
# or
uv add xtor
```

## Quick Start

```python
from xtor import Tor

with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    print(f"Connected through IP: {tor.ip}")
    resp = tor.client.get("https://api.ipify.org")
    print(resp.text)
```

## Usage

### Start a New Tor Process

```python
from xtor import Tor
from xtor.exceptions import TorNotFoundError, PortInUseError

try:
    with Tor.start(port=9052, control_port=9053, host="127.0.0.1", password="mypass") as tor:
        print(tor.ip)
        resp = tor.client.get("https://api.ipify.org")
        print(resp.text)
except TorNotFoundError:
    print("Tor not found on PATH")
except PortInUseError as e:
    print(f"Port in use: {e}")
```

> **Note:** `Tor.startTor()` is available as an alias for `Tor.start()` for backwards compatibility.

### Connect to an Existing Instance

```python
with Tor(password="mypass", port=9050, control_port=9051) as tor:
    print(tor.ip)
```

### New Identity

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    print(tor.ip)
    tor.new_identity(wait=True, timeout=30)
    print(tor.ip)  # New IP
```

### Async Client

```python
import asyncio
from xtor import Tor

async def main():
    with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
        async with tor.async_client as client:
            resp = await client.get("https://api.ipify.org")
            print(resp.text)

asyncio.run(main())
```

### Stream Isolation

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    # Each key gets its own circuit
    client_a = tor.isolated_client("session-a")
    client_b = tor.isolated_client("session-b")
    # Requests through client_a and client_b use different circuits
```

### Circuit Management

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    circuits = tor.get_circuits()
    for c in circuits:
        print(f"Circuit {c.id}: {c.status}, path: {c.path}")

    # Close a specific circuit
    tor.close_circuit(circuits[0].id)
```

### Exit Node Info

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    info = tor.exit_node
    if info:
        print(f"Exit: {info.nickname} ({info.country})")
        print(f"Flags: {info.flags}")
```

### Hidden Services

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    service = tor.create_hidden_service({80: 8080})
    print(f"Service: {service.onion_address}")

    # Remove when done
    tor.remove_hidden_service(service)
```

### Event Listeners

```python
with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
    def on_bandwidth(event):
        print(f"Read: {event.read}, Written: {event.written}")

    tor.add_event_listener("BW", on_bandwidth)
    # ... do work ...
    tor.remove_event_listener(on_bandwidth)
```

### TorPool

```python
from xtor import TorPool

with TorPool(size=3, base_port=9100, password="secret") as pool:
    # Round-robin
    tor = pool.next()
    print(tor.client.get("https://api.ipify.org").text)

    # Rotate all identities
    pool.rotate_all()

    # Random selection
    tor = pool.random()
```

### Named Instances (Python)

```python
from xtor import Tor

# Start named instance
tor = Tor.start(port=9052, control_port=9053, host="127.0.0.1", name="my-tor")

# Later, reconnect by name
tor = Tor.from_name("my-tor")
with tor:
    print(tor.ip)
```

## CLI Reference

The `xtor` CLI manages named Tor instances as background processes.

```bash
# Start a named instance
xtor start my-tor --port 9052 --control-port 9053

# List instances
xtor list

# Connection details
xtor connect my-tor

# Stop instance
xtor stop my-tor

# Remove instance and data
xtor remove my-tor
```

## Custom Exceptions

```
XtorError (base)
├── TorNotFoundError
├── PortInUseError
├── IdentityChangeTimeout
├── ConnectionError
└── AuthenticationError
```

Catch-all pattern:

```python
from xtor.exceptions import XtorError

try:
    with Tor.start(port=9052, control_port=9053, host="127.0.0.1") as tor:
        ...
except XtorError as e:
    print(f"xtor error: {e}")
```

## License

[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html)
