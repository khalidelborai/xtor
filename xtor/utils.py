"""Utility functions for xtor."""

import binascii
import hashlib
import os
import socket

from xtor.exceptions import PortInUseError

__all__ = ["get_tor_pass_hash", "is_port_available", "check_port_or_raise"]


def get_tor_pass_hash(secret_password: str) -> str:
    """
    Generate a hashed password for Tor control port authentication.

    Args:
        secret_password: The plaintext password to hash.

    Returns:
        A Tor-compatible hashed password string (format: 16:SALT+INDICATOR+HASH).

    Reference:
        https://stackoverflow.com/a/67198518
    """
    # Static 'count' value later referenced as "c"
    indicator = chr(96)
    # Generate salt and append indicator value
    salt_bytes = os.urandom(8)
    salt = salt_bytes.decode("latin-1") + indicator
    c = ord(indicator)

    # Generate an even number that can be divided in subsequent sections
    EXPBIAS = 6
    count = (16 + (c & 15)) << ((c >> 4) + EXPBIAS)

    d = hashlib.sha1()
    # Take the salt and append the password
    tmp = salt[:8] + secret_password

    # Hash the salty password
    slen = len(tmp)
    while count:
        if count > slen:
            d.update(tmp.encode("utf-8"))
            count -= slen
        else:
            d.update(tmp[:count].encode("utf-8"))
            count = 0

    hashed = d.digest()
    salt_res = binascii.b2a_hex(salt[:8].encode("utf-8")).upper().decode()
    indicator_res = binascii.b2a_hex(indicator.encode("utf-8")).upper().decode()
    tor_hash_res = binascii.b2a_hex(hashed).upper().decode()
    hashed_control_password = "16:" + salt_res + indicator_res + tor_hash_res

    return hashed_control_password


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if a port is available for binding.

    Args:
        port: The port number to check.
        host: The host address to check (default: 127.0.0.1).

    Returns:
        True if the port is available, False if it's in use.

    Raises:
        PortInUseError: If you want to raise instead of returning False,
            use check_port_or_raise() instead.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        return result != 0


def check_port_or_raise(port: int, host: str = "127.0.0.1") -> None:
    """
    Check if a port is available, raising an exception if not.

    Args:
        port: The port number to check.
        host: The host address to check (default: 127.0.0.1).

    Raises:
        PortInUseError: If the port is already in use.
    """
    if not is_port_available(port, host):
        raise PortInUseError(f"Port {port} is already in use on {host}")
