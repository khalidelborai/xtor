from __future__ import annotations

import functools
import secrets
import string
import time
from dataclasses import dataclass
from datetime import timedelta
from subprocess import Popen
from typing import Any, Callable

import httpx
from httpx import Client
from stem.control import Controller
from stem.process import launch_tor_with_config
from where import first as where

from xtor.exceptions import (
    AuthenticationError,
    ConnectionError,
    IdentityChangeTimeout,
    PortInUseError,
    TorNotFoundError,
)
from xtor.utils import get_tor_pass_hash, is_port_available

# Default IP check URL
DEFAULT_IP_CHECK_URL = "https://api.ipify.org"


def generate_password(length: int = 16) -> str:
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass
class HiddenService:
    """Information about an ephemeral hidden service."""

    hostname: str  # The .onion address
    ports: dict[int, tuple[str, int]]  # {virtual_port: (target_host, target_port)}
    private_key: str | None = None

    @property
    def onion_address(self) -> str:
        """Get the full .onion address."""
        return self.hostname if self.hostname.endswith(".onion") else f"{self.hostname}.onion"


@dataclass
class ExitNodeInfo:
    """Information about the current Tor exit node."""

    fingerprint: str
    nickname: str
    address: str
    country: str | None
    bandwidth: int | None  # bytes/sec
    flags: list[str]


class Tor:
    """
    Tor instance for managing Tor connections and HTTP clients.

    Can be used in two ways:
    1. Connect to an existing Tor instance via constructor
    2. Launch a new Tor process via Tor.start() class method

    Example:
        # Connect to existing Tor
        with Tor(password="mypass", port=9050, control_port=9051) as tor:
            print(tor.ip)

        # Launch new Tor process
        with Tor.start(port=9050, control_port=9051, host="127.0.0.1", password="mypass") as tor:
            response = tor.client.get("https://example.com")
    """

    def __init__(
        self,
        password: str,
        port: int = 9050,
        control_port: int = 9051,
        host: str | None = "127.0.0.1",
        client_options: dict[str, Any] | None = None,
        tor: Popen | None = None,
        ip_check_url: str = DEFAULT_IP_CHECK_URL,
        client_timeout: float = 30.0,
        name: str | None = None,
    ) -> None:
        """
        Initialize a Tor instance to connect to an existing Tor process.

        Args:
            password: Password for Tor control port authentication.
            port: SOCKS port for Tor proxy. Defaults to 9050.
            control_port: Control port for Tor commands. Defaults to 9051.
            host: Host address for Tor. Defaults to "127.0.0.1".
            client_options: Additional options to pass to httpx.Client. Defaults to None.
            tor: Existing Tor subprocess (used internally by start()). Defaults to None.
            ip_check_url: URL to use for IP address lookups. Defaults to "https://api.ipify.org".
            client_timeout: Timeout in seconds for HTTP client requests. Defaults to 30.0.
            name: Name for this instance (used for state persistence). Defaults to None.

        Raises:
            ConnectionError: If connection to the Tor control port fails.
        """
        self.port = port
        self.password = password
        self.control_port = control_port
        self.client_options = client_options or {}
        self.tor = tor
        self.host = host
        self.ip_check_url = ip_check_url
        self.client_timeout = client_timeout
        self.name = name

        # Connect to controller
        try:
            self.controller = Controller.from_port(port=self.control_port)
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Tor control port {self.control_port}: {e}"
            ) from e

    @staticmethod
    def start(
        port: int,
        control_port: int,
        host: str,
        password: str | None = None,
        client_options: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        path: str | None = None,
        own: bool | None = True,
        max_circuit_dirtiness: int | None = None,
        countries: list[str] | None = None,
        ip_check_url: str = DEFAULT_IP_CHECK_URL,
        client_timeout: float = 30.0,
        name: str | None = None,
        *args,
        **kwargs,
    ) -> Tor:
        """
        Start a new Tor process and return a connected Tor instance.

        Args:
            port: SOCKS port for Tor proxy.
            control_port: Control port for Tor commands.
            host: Host address for Tor.
            password: Password for Tor control port authentication. Defaults to None.
            client_options: Additional options to pass to httpx.Client. Defaults to None.
            config: Additional Tor configuration options. Defaults to None.
            path: Path to tor binary. If None, searches system PATH.
            own: Assert ownership over Tor process (aborts if Python terminates). Defaults to True.
            max_circuit_dirtiness: Maximum time in seconds a circuit can be reused. Minimum 10.
            countries: List of country codes for exit nodes (e.g., ["US", "DE"]).
            ip_check_url: URL to use for IP address lookups. Defaults to "https://api.ipify.org".
            client_timeout: Timeout in seconds for HTTP client requests. Defaults to 30.0.
            name: Name for this instance (for state persistence). Defaults to None.
            *args: Additional positional arguments for launch_tor_with_config.
            **kwargs: Additional keyword arguments for launch_tor_with_config.

        Raises:
            TorNotFoundError: If tor binary cannot be found.
            PortInUseError: If the requested port is already in use.

        Returns:
            Tor: Connected Tor instance.
        """
        # Handle mutable defaults
        client_options = client_options or {}
        config = config or {}

        # Generate password if not provided
        password = password or generate_password()

        # Find tor binary
        if path is not None:
            kwargs["tor_cmd"] = path
        else:
            tor_path = where("tor")
            if tor_path is None:
                raise TorNotFoundError(
                    "Tor binary not found. Please install Tor or specify path."
                )
            kwargs["tor_cmd"] = tor_path

        # Check port availability
        if not is_port_available(port, host):
            raise PortInUseError(f"Port {port} is already in use")
        if not is_port_available(control_port, host):
            raise PortInUseError(f"Control port {control_port} is already in use")

        # Set up data directory for named instances
        data_dir = None
        if name:
            from xtor.state import get_instance_data_dir

            data_dir = get_instance_data_dir(name)

        # Build Tor configuration
        tor_config: dict[str, str] = {
            "SocksPort": str(port),
            "ControlPort": str(control_port),
            **{k: str(v) if not isinstance(v, str) else v for k, v in config.items()},
        }

        if data_dir:
            tor_config["DataDirectory"] = str(data_dir)

        tor_config["HashedControlPassword"] = get_tor_pass_hash(password)

        if max_circuit_dirtiness is not None and max_circuit_dirtiness >= 10:
            tor_config["MaxCircuitDirtiness"] = str(max_circuit_dirtiness)

        if countries is not None:
            tor_config["ExitNodes"] = "{" + ",".join(countries) + "}"

        # Launch Tor process
        tor_process: Popen = launch_tor_with_config(
            config=tor_config,
            take_ownership=own,
            *args,
            **kwargs,
        )

        # Save state for named instances
        if name:
            from xtor.state import InstanceState, save_instance

            save_instance(
                InstanceState(
                    name=name,
                    pid=tor_process.pid if tor_process else None,
                    port=port,
                    control_port=control_port,
                    password=password,
                    host=host,
                    data_dir=str(data_dir) if data_dir else None,
                )
            )

        return Tor(
            password=password,
            port=port,
            control_port=control_port,
            client_options=client_options,
            tor=tor_process,
            host=host,
            ip_check_url=ip_check_url,
            client_timeout=client_timeout,
            name=name,
        )

    # Keep old name as alias for backwards compatibility
    startTor = start

    @classmethod
    def from_name(cls, name: str) -> Tor:
        """
        Connect to an existing named Tor instance.

        Args:
            name: Name of the instance to connect to.

        Returns:
            Tor: Connected Tor instance.

        Raises:
            ValueError: If instance not found.
        """
        from xtor.state import get_instance

        instance = get_instance(name)
        if instance is None:
            raise ValueError(f"Instance '{name}' not found")

        return cls(
            password=instance.password,
            port=instance.port,
            control_port=instance.control_port,
            host=instance.host,
            name=name,
        )

    @functools.cached_property
    def client(self) -> Client:
        """
        Get pre-configured httpx Client with SOCKS5 proxy.

        Returns:
            Client: httpx Client configured to use Tor proxy.
        """
        return Client(
            **self.client_options,
            proxy=f"socks5h://{self.host}:{self.port}",
            timeout=self.client_timeout,
        )

    @functools.cached_property
    def async_client(self) -> httpx.AsyncClient:
        """
        Get pre-configured async httpx Client with SOCKS5h proxy.

        Returns:
            AsyncClient: httpx AsyncClient configured to use Tor proxy.
        """
        return httpx.AsyncClient(
            **self.client_options,
            proxy=f"socks5h://{self.host}:{self.port}",
            timeout=self.client_timeout,
        )

    def isolated_client(self, isolation_key: str) -> Client:
        """
        Get an HTTP client with stream isolation.

        Different isolation keys use different Tor circuits, preventing
        traffic correlation between requests.

        Args:
            isolation_key: Unique key for circuit isolation. Same key = same circuit.

        Returns:
            Client: httpx Client with isolated circuit.
        """
        return Client(
            **self.client_options,
            proxy=f"socks5h://{isolation_key}:{isolation_key}@{self.host}:{self.port}",
            timeout=self.client_timeout,
        )

    def isolated_async_client(self, isolation_key: str) -> httpx.AsyncClient:
        """
        Get an async HTTP client with stream isolation.

        Args:
            isolation_key: Unique key for circuit isolation.

        Returns:
            AsyncClient: httpx AsyncClient with isolated circuit.
        """
        return httpx.AsyncClient(
            **self.client_options,
            proxy=f"socks5h://{isolation_key}:{isolation_key}@{self.host}:{self.port}",
            timeout=self.client_timeout,
        )

    def connect(self) -> None:
        """
        Authenticate with the Tor controller.

        Raises:
            AuthenticationError: If authentication fails.
        """
        try:
            self.controller.authenticate(password=self.password)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to authenticate with Tor controller: {e}"
            ) from e

    def disconnect(self) -> None:
        """
        Close the Tor controller connection.
        """
        self.controller.close()

    def __enter__(self) -> Tor:
        """
        Enter context manager - authenticates with controller.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit context manager - closes controller and HTTP client.
        """
        self.disconnect()
        # Close HTTP client if it was created
        if "client" in self.__dict__:
            self.client.close()
        # Note: async_client requires await to close properly
        # User should close it manually or use async context manager
        if "async_client" in self.__dict__:
            # Can't await in sync __exit__, user should close manually or use async context
            pass

    def _fetch_ip(self, retries: int = 3) -> str:
        """
        Fetch current IP address through Tor.

        Args:
            retries: Number of retry attempts for transient failures. Defaults to 3.

        Returns:
            str: Current IP address as seen through Tor.

        Raises:
            httpx.HTTPError: If all retry attempts fail.
        """
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                return self.client.get(self.ip_check_url).text.strip()
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                continue
        if last_error is not None:
            raise last_error
        raise httpx.NetworkError("Failed to fetch IP after retries")

    @functools.cached_property
    def ip(self) -> str:
        """
        Get connected instance IP address.

        Returns:
            str: Current IP address as seen through Tor.
        """
        return self._fetch_ip()

    def new_identity(
        self,
        wait: bool = False,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> None:
        """
        Request a new Tor identity (new circuit/IP).

        Args:
            wait: If True, wait until IP actually changes. Defaults to False.
            timeout: Maximum time in seconds to wait for IP change. Defaults to 30.0.
            poll_interval: Time in seconds between IP checks. Defaults to 0.5.

        Raises:
            IdentityChangeTimeout: If wait=True and IP doesn't change within timeout.
        """
        self.controller.signal("NEWNYM")

        if wait:
            old_ip = self._fetch_ip()
            start_time = time.monotonic()

            while True:
                time.sleep(poll_interval)
                new_ip = self._fetch_ip()

                if new_ip != old_ip:
                    # Clear cached IP so next access gets fresh value
                    if "ip" in self.__dict__:
                        del self.__dict__["ip"]
                    return

                elapsed = time.monotonic() - start_time
                if elapsed >= timeout:
                    raise IdentityChangeTimeout(
                        f"IP did not change after {timeout} seconds. "
                        f"Current IP: {new_ip}"
                    )
        else:
            # Clear cached IP so next access gets fresh value
            if "ip" in self.__dict__:
                del self.__dict__["ip"]

    def kill(self) -> None:
        """
        Kill the Tor process (if started via start()).

        Does nothing if no Tor process is associated with this instance.
        """
        if self.tor is not None:
            self.tor.kill()

    def terminate(self) -> None:
        """
        Terminate the Tor process gracefully (if started via start()).

        Does nothing if no Tor process is associated with this instance.
        """
        if self.tor is not None:
            self.tor.terminate()

    def stop(self) -> None:
        """
        Stop a named instance and remove from state.

        For unnamed instances, same as terminate().
        """
        if self.name:
            from xtor.state import remove_instance

            remove_instance(self.name)

        if self.tor is not None:
            self.tor.terminate()

    # -------------------------------------------------------------------------
    # Status/Health Monitoring Properties
    # -------------------------------------------------------------------------

    @property
    def version(self) -> str:
        """Get Tor version string."""
        return str(self.controller.get_version())

    @property
    def uptime(self) -> timedelta:
        """Get Tor process uptime."""
        return self.controller.get_uptime()

    @property
    def can_new_identity(self) -> bool:
        """Check if new identity request is available (rate limited to 10s)."""
        return self.controller.is_newnym_available()

    @property
    def newnym_wait(self) -> float:
        """Get seconds until new identity request is available."""
        return self.controller.get_newnym_wait()

    @property
    def is_alive(self) -> bool:
        """Check if Tor controller connection is alive."""
        return self.controller.is_alive()

    # -------------------------------------------------------------------------
    # Event Listener Methods
    # -------------------------------------------------------------------------

    def add_event_listener(
        self,
        event_type: str,
        callback: Callable,
    ) -> None:
        """
        Subscribe to Tor controller events.

        Args:
            event_type: Event type to listen for. Common types:
                - "CIRC": Circuit events (built, closed, failed)
                - "STREAM": Stream events (new connections)
                - "BW": Bandwidth events (bytes read/written)
                - "NEWDESC": New relay descriptors
                - "ADDRMAP": Address mapping events
                - "SIGNAL": Signal events
            callback: Function to call when event occurs. Receives event object.

        Example:
            def on_circuit(event):
                print(f"Circuit {event.id}: {event.status}")

            tor.add_event_listener("CIRC", on_circuit)
        """
        from stem.control import EventType

        # Convert string to EventType enum if needed
        if isinstance(event_type, str):
            event_type = EventType(event_type)

        self.controller.add_event_listener(callback, event_type)

    def remove_event_listener(self, callback: Callable) -> None:
        """
        Remove an event listener callback.

        Args:
            callback: The callback function to remove.
        """
        self.controller.remove_event_listener(callback)

    # -------------------------------------------------------------------------
    # Circuit Management
    # -------------------------------------------------------------------------

    def get_circuits(self) -> list:
        """
        Get all current Tor circuits.

        Returns:
            list: List of Circuit objects from stem with attributes:
                - id: Circuit ID
                - status: Circuit status (BUILT, EXTENDED, etc.)
                - path: List of (fingerprint, nickname) tuples for relays
                - purpose: Circuit purpose (GENERAL, HS_CLIENT, etc.)
        """
        return self.controller.get_circuits()

    def close_circuit(self, circuit_id: str | int) -> None:
        """
        Close a specific Tor circuit.

        Args:
            circuit_id: The circuit ID to close.
        """
        self.controller.close_circuit(str(circuit_id))

    def get_streams(self) -> list:
        """
        Get all current Tor streams.

        Returns:
            list: List of stream info with target addresses and circuit IDs.
        """
        return self.controller.get_streams()

    def attach_stream(self, stream_id: str | int, circuit_id: str | int) -> None:
        """
        Attach a stream to a specific circuit.

        Args:
            stream_id: The stream ID to attach.
            circuit_id: The circuit ID to attach to.
        """
        self.controller.attach_stream(str(stream_id), str(circuit_id))

    def get_exit_node_info(self) -> ExitNodeInfo | None:
        """
        Get detailed information about the current exit node.

        Returns:
            ExitNodeInfo: Exit node details including country, bandwidth, flags.
            None: If no circuit is available or exit node info cannot be determined.
        """
        circuits = self.controller.get_circuits()

        # Find a built general-purpose circuit
        for circuit in circuits:
            if circuit.status == "BUILT" and circuit.path:
                # Exit node is the last relay in the path
                exit_fingerprint, exit_nickname = circuit.path[-1]

                try:
                    # Get relay info from network status
                    relay = self.controller.get_network_status(exit_fingerprint)

                    # Try to get country via GeoIP (may not be available)
                    country = None
                    try:
                        country = self.controller.get_info(f"ip-to-country/{relay.address}")
                    except Exception:
                        pass

                    return ExitNodeInfo(
                        fingerprint=exit_fingerprint,
                        nickname=exit_nickname,
                        address=relay.address,
                        country=country,
                        bandwidth=relay.bandwidth if hasattr(relay, "bandwidth") else None,
                        flags=list(relay.flags) if hasattr(relay, "flags") else [],
                    )
                except Exception:
                    continue

        return None

    @property
    def exit_node(self) -> ExitNodeInfo | None:
        """Get current exit node information."""
        return self.get_exit_node_info()

    # -------------------------------------------------------------------------
    # Hidden Service Methods
    # -------------------------------------------------------------------------

    def create_hidden_service(
        self,
        ports: dict[int, int | tuple[str, int]],
        key_type: str = "NEW",
        key_content: str = "ED25519-V3",
        discard_key: bool = False,
        detached: bool = False,
        await_publication: bool = False,
    ) -> HiddenService:
        """
        Create an ephemeral hidden service (.onion address).

        Args:
            ports: Port mapping. Keys are virtual ports (what clients connect to),
                values are target ports or (host, port) tuples.
                Example: {80: 8080} or {80: ("127.0.0.1", 8080)}
            key_type: Key type, "NEW" for new key or "ED25519-V3"/"RSA1024" for existing.
            key_content: Key content or "ED25519-V3"/"RSA1024" for new key generation.
            discard_key: If True, don't return private key (more secure, but can't recreate).
            detached: If True, service persists after controller disconnects.
            await_publication: If True, wait for service to be published to HSDir.

        Returns:
            HiddenService: The created hidden service with hostname and ports.

        Example:
            # Create service mapping .onion:80 -> localhost:8080
            service = tor.create_hidden_service({80: 8080})
            print(f"Service at: {service.onion_address}")
        """
        # Normalize ports to stem format
        port_mappings = {}
        for virtual_port, target in ports.items():
            if isinstance(target, int):
                port_mappings[virtual_port] = f"127.0.0.1:{target}"
            else:
                host, port = target
                port_mappings[virtual_port] = f"{host}:{port}"

        response = self.controller.create_ephemeral_hidden_service(
            ports=port_mappings,
            key_type=key_type,
            key_content=key_content,
            discard_key=discard_key,
            detached=detached,
            await_publication=await_publication,
        )

        # Build ports dict for HiddenService
        parsed_ports = {}
        for virtual_port, target in ports.items():
            if isinstance(target, int):
                parsed_ports[virtual_port] = ("127.0.0.1", target)
            else:
                parsed_ports[virtual_port] = target

        return HiddenService(
            hostname=response.hostname,
            ports=parsed_ports,
            private_key=response.private_key if not discard_key else None,
        )

    def remove_hidden_service(self, service: HiddenService | str) -> None:
        """
        Remove an ephemeral hidden service.

        Args:
            service: HiddenService object or .onion hostname string.
        """
        hostname = service.hostname if isinstance(service, HiddenService) else service
        # Remove .onion suffix if present
        if hostname.endswith(".onion"):
            hostname = hostname[:-6]
        self.controller.remove_ephemeral_hidden_service(hostname)

    def list_hidden_services(self) -> list[str]:
        """
        List hostnames of active ephemeral hidden services.

        Returns:
            list[str]: List of .onion hostnames.
        """
        return self.controller.list_ephemeral_hidden_services()
