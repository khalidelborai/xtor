"""xtor - Python library for managing Tor instances programmatically."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("xtor")
except PackageNotFoundError:
    __version__ = "unknown"

from xtor.exceptions import (
    AuthenticationError,
    ConnectionError,
    IdentityChangeTimeout,
    PortInUseError,
    TorNotFoundError,
    XtorError,
)
from xtor.pool import TorPool
from xtor.state import InstanceState
from xtor.tor import ExitNodeInfo, HiddenService, Tor
from xtor.utils import get_tor_pass_hash, is_port_available

__all__ = [
    "__version__",
    "Tor",
    "TorPool",
    "InstanceState",
    "HiddenService",
    "ExitNodeInfo",
    "get_tor_pass_hash",
    "is_port_available",
    "XtorError",
    "TorNotFoundError",
    "PortInUseError",
    "IdentityChangeTimeout",
    "ConnectionError",
    "AuthenticationError",
]
