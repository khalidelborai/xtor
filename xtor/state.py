import json
import os
import shutil
from pathlib import Path
import stat

XTOR_DIR = Path.home() / ".xtor"
INSTANCES_DIR = XTOR_DIR / "instances"
STATE_FILE = XTOR_DIR / "state.json"

def ensure_xtor_dir():
    """Create the ~/.xtor directory if it doesn't exist and set secure permissions."""
    if not XTOR_DIR.exists():
        XTOR_DIR.mkdir()
        XTOR_DIR.chmod(0o700)
    if not INSTANCES_DIR.exists():
        INSTANCES_DIR.mkdir()
        INSTANCES_DIR.chmod(0o700)

def read_state() -> dict:
    """Read the state file and return its content."""
    ensure_xtor_dir()
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def write_state(state: dict):
    """Write the state dictionary to the state file with secure permissions."""
    ensure_xtor_dir()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    STATE_FILE.chmod(0o600)

def create_instance_dir(name: str) -> Path:
    """Create a data directory for a named instance."""
    ensure_xtor_dir()
    instance_dir = INSTANCES_DIR / name
    if not instance_dir.exists():
        instance_dir.mkdir()
        instance_dir.chmod(0o700)
    return instance_dir

def remove_instance_dir(name: str):
    """Remove the data directory for a named instance."""
    instance_dir = INSTANCES_DIR / name
    if instance_dir.exists():
        shutil.rmtree(instance_dir)
