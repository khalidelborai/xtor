"""TorPool - Manage multiple Tor instances for high-throughput applications."""

from __future__ import annotations

import itertools
import random
from typing import Iterator

from xtor.tor import Tor


class TorPool:
    """
    Pool of Tor instances for parallel requests with automatic port allocation.

    Manages multiple Tor processes with round-robin or random selection,
    automatic port allocation, and bulk identity rotation.

    Example:
        with TorPool(size=3, base_port=9100, password="secret") as pool:
            # Round-robin selection
            for url in urls:
                tor = pool.next()
                response = tor.client.get(url)

            # Rotate all identities
            pool.rotate_all()

            # Random selection
            tor = pool.random()
    """

    def __init__(
        self,
        size: int,
        base_port: int = 9100,
        password: str | None = None,
        host: str = "127.0.0.1",
        countries: list[str] | None = None,
        client_timeout: float = 30.0,
    ) -> None:
        """
        Initialize a Tor pool.

        Args:
            size: Number of Tor instances to manage.
            base_port: Starting port for SOCKS proxies. Control ports start at base_port + 100.
            password: Password for Tor control ports.
            host: Host address for Tor instances.
            countries: List of country codes for exit nodes.
            client_timeout: HTTP client timeout in seconds.
        """
        self.size = size
        self.base_port = base_port
        self.password = password
        self.host = host
        self.countries = countries
        self.client_timeout = client_timeout

        self._instances: list[Tor] = []
        self._cycle: Iterator[Tor] | None = None

    def start(self) -> TorPool:
        """
        Start all Tor instances in the pool.

        Returns:
            TorPool: Self for method chaining.
        """
        for i in range(self.size):
            port = self.base_port + i
            control_port = self.base_port + 100 + i

            tor = Tor.start(
                port=port,
                control_port=control_port,
                host=self.host,
                password=self.password,
                countries=self.countries,
                client_timeout=self.client_timeout,
            )
            tor.connect()
            self._instances.append(tor)

        self._cycle = itertools.cycle(self._instances)
        return self

    def stop(self) -> None:
        """Stop all Tor instances in the pool."""
        for tor in self._instances:
            try:
                tor.disconnect()
                tor.terminate()
            except Exception:
                pass
        self._instances.clear()
        self._cycle = None

    def __enter__(self) -> TorPool:
        """Enter context manager - starts all instances."""
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - stops all instances."""
        self.stop()

    def next(self) -> Tor:
        """
        Get next Tor instance using round-robin selection.

        Returns:
            Tor: Next Tor instance in rotation.
        """
        if not self._cycle:
            raise RuntimeError("Pool not started. Use 'with TorPool(...) as pool:' or call start()")
        return next(self._cycle)

    def random(self) -> Tor:
        """
        Get a random Tor instance from the pool.

        Returns:
            Tor: Random Tor instance.
        """
        if not self._instances:
            raise RuntimeError("Pool not started")
        return random.choice(self._instances)

    def get(self, index: int) -> Tor:
        """
        Get a specific Tor instance by index.

        Args:
            index: Instance index (0 to size-1).

        Returns:
            Tor: Tor instance at the given index.
        """
        return self._instances[index]

    def rotate_all(self, wait: bool = False, timeout: float = 30.0) -> None:
        """
        Request new identity on all Tor instances.

        Args:
            wait: If True, wait for IP to change on each instance.
            timeout: Maximum seconds to wait per instance.
        """
        for tor in self._instances:
            tor.new_identity(wait=wait, timeout=timeout)

    def rotate_one(self, wait: bool = False, timeout: float = 30.0) -> Tor:
        """
        Rotate identity on one instance (the next in round-robin).

        Args:
            wait: If True, wait for IP to change.
            timeout: Maximum seconds to wait.

        Returns:
            Tor: The rotated instance.
        """
        tor = self.next()
        tor.new_identity(wait=wait, timeout=timeout)
        return tor

    @property
    def instances(self) -> list[Tor]:
        """Get all Tor instances in the pool."""
        return self._instances.copy()

    @property
    def ips(self) -> list[str]:
        """Get IP addresses of all instances."""
        return [tor.ip for tor in self._instances]

    def __len__(self) -> int:
        """Get number of instances in pool."""
        return len(self._instances)

    def __iter__(self) -> Iterator[Tor]:
        """Iterate over all instances."""
        return iter(self._instances)
