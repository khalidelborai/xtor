import os
import time
from pathlib import Path
import pytest
from xtor.tor import Tor
from xtor.state import read_state, remove_instance_dir, XTOR_DIR

TEST_INSTANCE_NAME = "test_instance"

@pytest.fixture(scope="module", autouse=True)
def cleanup_xtor_dir():
    """Ensure the ~/.xtor directory is clean before and after tests."""
    if XTOR_DIR.exists():
        # Clean up any old state before running tests
        for f in XTOR_DIR.glob("*"):
            if f.is_file():
                f.unlink()
            else:
                os.system(f"rm -rf {f}")
    yield
    if XTOR_DIR.exists():
        # Clean up after tests
        for f in XTOR_DIR.glob("*"):
            if f.is_file():
                f.unlink()
            else:
                os.system(f"rm -rf {f}")


def test_create_and_manage_instance():
    """Test the full lifecycle of a managed instance."""
    # 1. Create a new managed instance
    instance = Tor.create(
        name=TEST_INSTANCE_NAME,
        host="127.0.0.1",
        port=19052,
        control_port=19053,
        own=False
    )
    assert instance.tor is not None
    assert instance.tor.pid is not None

    # Give Tor a moment to start
    time.sleep(5)

    # 2. Check that its state is recorded
    state = read_state()
    assert TEST_INSTANCE_NAME in state
    assert state[TEST_INSTANCE_NAME]["pid"] == instance.tor.pid
    assert state[TEST_INSTANCE_NAME]["port"] == 19052

    # 3. Connect to the instance using its name
    connected_instance = Tor.from_name(TEST_INSTANCE_NAME)
    with connected_instance as tor:
        assert tor.controller.is_alive()
        # Check we get a valid IP
        assert "." in tor.ip

    # 4. Stop the instance
    connected_instance.stop()
    time.sleep(2) # Give it a moment to terminate

    # 5. Check that its state is removed
    state = read_state()
    assert TEST_INSTANCE_NAME not in state

    # Verify the process is gone
    import psutil
    assert not psutil.pid_exists(instance.tor.pid)

    # 6. Remove its data directory
    remove_instance_dir(TEST_INSTANCE_NAME)
    instance_dir = XTOR_DIR / "instances" / TEST_INSTANCE_NAME
    assert not instance_dir.exists()
