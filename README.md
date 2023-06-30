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
```
