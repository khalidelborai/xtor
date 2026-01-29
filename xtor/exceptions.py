"""Custom exceptions for xtor."""

__all__ = [
    "XtorError",
    "TorNotFoundError",
    "PortInUseError",
    "IdentityChangeTimeout",
    "ConnectionError",
    "AuthenticationError",
]


class XtorError(Exception):
    """Base exception for all xtor errors."""


class TorNotFoundError(XtorError):
    """Raised when tor binary cannot be found on system PATH."""


class PortInUseError(XtorError):
    """Raised when the requested port is already in use."""


class IdentityChangeTimeout(XtorError):
    """Raised when new identity request times out."""


class ConnectionError(XtorError):
    """Raised when connection to Tor control port fails."""


class AuthenticationError(XtorError):
    """Raised when authentication to Tor control port fails."""
