"""State management for named Tor instances."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

__all__ = [
    "InstanceState",
    "get_xtor_dir",
    "get_instances_dir",
    "read_state",
    "write_state",
    "get_instance",
    "save_instance",
    "remove_instance",
    "list_instances",
    "get_instance_data_dir",
    "remove_instance_data_dir",
]

# Default paths
XTOR_DIR = Path.home() / ".xtor"
INSTANCES_DIR = XTOR_DIR / "instances"
STATE_FILE = XTOR_DIR / "state.json"


@dataclass
class InstanceState:
    """State for a named Tor instance."""
    name: str
    pid: int | None
    port: int
    control_port: int
    password: str
    host: str = "127.0.0.1"
    data_dir: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, name: str, data: dict) -> InstanceState:
        return cls(
            name=name,
            pid=data.get("pid"),
            port=data["port"],
            control_port=data["control_port"],
            password=data["password"],
            host=data.get("host", "127.0.0.1"),
            data_dir=data.get("data_dir"),
        )


def get_xtor_dir() -> Path:
    """Get the xtor config directory, creating if needed."""
    if not XTOR_DIR.exists():
        XTOR_DIR.mkdir(mode=0o700)
    return XTOR_DIR


def get_instances_dir() -> Path:
    """Get the instances data directory, creating if needed."""
    get_xtor_dir()
    if not INSTANCES_DIR.exists():
        INSTANCES_DIR.mkdir(mode=0o700)
    return INSTANCES_DIR


def read_state() -> dict[str, dict]:
    """Read all instance state from disk."""
    get_xtor_dir()
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def write_state(state: dict[str, dict]) -> None:
    """Write instance state to disk with secure permissions."""
    get_xtor_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    STATE_FILE.chmod(0o600)


def get_instance(name: str) -> InstanceState | None:
    """Get a specific instance's state."""
    state = read_state()
    if name not in state:
        return None
    return InstanceState.from_dict(name, state[name])


def save_instance(instance: InstanceState) -> None:
    """Save an instance's state."""
    state = read_state()
    data = instance.to_dict()
    del data["name"]  # Name is the key, not stored in value
    state[instance.name] = data
    write_state(state)


def remove_instance(name: str) -> bool:
    """Remove an instance from state. Returns True if found and removed."""
    state = read_state()
    if name not in state:
        return False
    del state[name]
    write_state(state)
    return True


def list_instances() -> list[InstanceState]:
    """List all saved instances."""
    state = read_state()
    return [InstanceState.from_dict(name, data) for name, data in state.items()]


def get_instance_data_dir(name: str) -> Path:
    """Get or create the data directory for a named instance."""
    instance_dir = get_instances_dir() / name
    if not instance_dir.exists():
        instance_dir.mkdir(mode=0o700)
    return instance_dir


def remove_instance_data_dir(name: str) -> bool:
    """Remove the data directory for a named instance."""
    import shutil
    instance_dir = get_instances_dir() / name
    if instance_dir.exists():
        shutil.rmtree(instance_dir)
        return True
    return False
