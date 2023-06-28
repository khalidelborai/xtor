xtor
===============================

Torx is a simple tool for managing Tor instances.

- `sudo apt-get install obfs4proxy`
- `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-x86_64.tar.gz`
- `https://archive.torproject.org/tor-package-archive/torbrowser/12.5a6/tor-expert-bundle-12.5a6-windows-i686.tar.gz`
  - `ServerTransportPlugin obfs3,obfs4 exec /usr/bin/obfs4proxy`
- `sudo apt-get install tor`
  - `SocksPort 0`
  - `ControlPort 9051`
  - `ExitNodes {us}`
  - `StrictNodes 1`
  - `DataDirectory /var/lib/tor`
  - `BridgeRelay 1`
  - `Bridge obfs4`
  - `Bridges <IP>:<PORT> <IP>:<PORT> <IP>:<PORT> <IP>:<PORT>`
  
