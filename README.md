xtor
===============================

xtor is a simple tool for managing Tor instances.

**Requirements:** Python 3.10+

## Installation

- Linux
  - `sudo apt-get install tor`
  - `sudo apt-get install obfs4proxy`

- Windows
  - Download and install Tor Expert Bundle
    - `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-x86_64.tar.gz`
    - `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-i686.tar.gz`

Then install the python package:

```bash
# Using pip
pip install xtor

# Using uv
uv add xtor
```

## Usage

```python
from xtor import Tor
from xtor.exceptions import TorNotFoundError, PortInUseError, IdentityChangeTimeout

# Start a new Tor process
try:
    with Tor.start(
        port=9052,
        control_port=9053,
        host="127.0.0.1",
        password="passw0rd",
        init_msg_handler=print,
        path="/usr/bin/tor",  # optional, primarily for windows
    ) as tor:
        print(tor.ip)
        print(tor.client.get("https://api.ipify.org").text)
except TorNotFoundError:
    print("Tor binary not found on system PATH")
except PortInUseError as e:
    print(f"Port already in use: {e}")


# Connect to an existing Tor instance
with Tor(
    port=9052,
    control_port=9053,
    host="127.0.0.1",
    password="passw0rd",
) as tor:
    print(tor.ip)
    print(tor.client.get("https://api.ipify.org").text)

    try:
        tor.new_identity(wait=True)  # get a new identity and wait for it to be ready
        print(tor.ip)
    except IdentityChangeTimeout:
        print("Timed out waiting for new IP address")
```

Note: `Tor.startTor()` is still available as an alias for backwards compatibility.

## CLI

```bash
xtor --help
```
