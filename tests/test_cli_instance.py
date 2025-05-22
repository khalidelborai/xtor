import pytest
import json
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, ANY

from xtor.cli import app # Main Typer app
from xtor.config_manager import ConfigManager # To mock its methods or instances

runner = CliRunner()

# Default parameters used for instance creation in tests for consistency
DEFAULT_TEST_PARAMS = {
    "port": 9050,
    "host": "127.0.0.1",
    "control_port": 9051,
    "password": "testpassword",
    "path": "/usr/bin/tor",
    "countries": ["US", "GB"],
    "max_circuit_dirtiness": 600,
    "own": True,
    "client_options": {},
    "torrc_config": {}
}

@pytest.fixture(autouse=True)
def isolate_config_manager_for_cli(tmp_path, monkeypatch):
    """
    Automatically mocks the global config_manager instance in xtor.cli
    to use a temporary directory for its configuration file.
    This ensures that CLI tests do not interfere with actual user configs
    or with other tests.
    """
    temp_config_dir = tmp_path / "cli_test_config" / "xtor"
    # No need to mkdir here, ConfigManager constructor handles it.
    
    # Create a new ConfigManager instance that uses the temp directory
    isolated_cm = ConfigManager(config_dir=temp_config_dir)
    
    # Monkeypatch the 'config_manager' instance in the 'xtor.cli' module
    monkeypatch.setattr('xtor.cli.config_manager', isolated_cm)
    
    # Also patch the Tor.from_config_id to use this isolated_cm if it were to be called
    # (though for start --instance-id, we mock Tor.startTor directly)
    # This might be useful if other commands directly use Tor.from_config_id
    def mock_from_config_id(cls, instance_id, config_manager_arg):
        # Ensure the CLI is using the isolated_cm when it calls Tor.from_config_id
        # For the `start` command, this might not be hit if we mock Tor.startTor itself.
        # However, if future CLI commands use Tor.from_config_id directly, this helps.
        return cls.startTor(**isolated_cm.load_config(instance_id))

    # It's tricky to patch Tor.from_config_id to *use* isolated_cm by default
    # because it's a static method. The CLI commands should pass the patched
    # config_manager to it. The `start` command in CLI already uses the
    # global `config_manager` which we've patched.

    # For PID files, ensure they also go to a temporary location
    pid_cache_dir = tmp_path / "cli_test_pid_cache" / "xtor"
    pid_cache_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr('xtor.cli.Path.home', lambda: pid_cache_dir.parent.parent) # Make Path.home() / ".cache" point to tmp_path / "cli_test_pid_cache"
    
    return isolated_cm # The test can use this to interact with the patched CM

# --- Tests for `xtor instance` subcommands ---

def test_instance_create(isolated_config_manager: ConfigManager):
    """Test `xtor instance create --id test_id --port 1234 ...`"""
    instance_id = "test_create_id"
    port = 1234
    host = "testhost"
    
    # Mock the save_config method of the isolated_config_manager
    # isolated_config_manager is the one patched into xtor.cli
    with patch.object(isolated_config_manager, 'save_config', wraps=isolated_config_manager.save_config) as mock_save:
        result = runner.invoke(app, [
            "instance", "create", "--id", instance_id,
            "--port", str(port), "--host", host,
            "--control-port", str(DEFAULT_TEST_PARAMS["control_port"]),
            "--password", DEFAULT_TEST_PARAMS["password"],
            "--path", DEFAULT_TEST_PARAMS["path"],
            "--countries", ",".join(DEFAULT_TEST_PARAMS["countries"]),
            "--max-time", str(DEFAULT_TEST_PARAMS["max_circuit_dirtiness"]),
            "--no-own" # Testing a boolean flag override
        ])

    assert result.exit_code == 0, result.stdout
    assert f"Configuration for instance '{instance_id}' created" in result.stdout
    
    mock_save.assert_called_once()
    # Check the actual arguments passed to save_config
    saved_args = mock_save.call_args[0]
    assert saved_args[0] == instance_id
    assert saved_args[1]["port"] == port
    assert saved_args[1]["host"] == host
    assert saved_args[1]["own"] is False # Check boolean flag
    assert saved_args[1]["countries"] == DEFAULT_TEST_PARAMS["countries"]

def test_instance_list_empty(isolated_config_manager: ConfigManager):
    """Test `xtor instance list` when no configs exist."""
    with patch.object(isolated_config_manager, 'list_configs', return_value={}) as mock_list:
        result = runner.invoke(app, ["instance", "list"])
    
    assert result.exit_code == 0, result.stdout
    assert "No instance configurations found." in result.stdout
    mock_list.assert_called_once()

def test_instance_list_with_configs(isolated_config_manager: ConfigManager):
    """Test `xtor instance list` with some mock configs."""
    configs_data = {
        "id1": {"port": 9050, "host": "localhost", "countries": ["DE"]},
        "id2": {"port": 9060, "host": "other_host", "countries": ["FR", "CA"]}
    }
    with patch.object(isolated_config_manager, 'list_configs', return_value=configs_data):
        result = runner.invoke(app, ["instance", "list"])

    assert result.exit_code == 0, result.stdout
    assert "Instance ID: id1" in result.stdout
    assert '"port": 9050' in result.stdout
    assert '"countries": "DE"' in result.stdout # Check string conversion
    assert "Instance ID: id2" in result.stdout
    assert '"port": 9060' in result.stdout
    assert '"countries": "FR,CA"' in result.stdout

def test_instance_delete(isolated_config_manager: ConfigManager):
    """Test `xtor instance delete --id test_id`."""
    instance_id = "test_delete_id"
    # Ensure delete_config returns True for successful deletion
    with patch.object(isolated_config_manager, 'delete_config', return_value=True) as mock_delete:
        result = runner.invoke(app, ["instance", "delete", "--id", instance_id])

    assert result.exit_code == 0, result.stdout
    assert f"Configuration for instance '{instance_id}' deleted successfully." in result.stdout
    mock_delete.assert_called_with(instance_id)

def test_instance_delete_not_found(isolated_config_manager: ConfigManager):
    """Test deleting a non-existent instance."""
    instance_id = "non_existent_id"
    with patch.object(isolated_config_manager, 'delete_config', return_value=False) as mock_delete:
        result = runner.invoke(app, ["instance", "delete", "--id", instance_id])
    
    assert result.exit_code == 0, result.stdout # Command itself succeeds but prints error
    assert f"Configuration for instance '{instance_id}' not found." in result.stdout
    mock_delete.assert_called_with(instance_id)


def test_instance_update(isolated_config_manager: ConfigManager):
    """Test `xtor instance update --id test_id --port 5678`."""
    instance_id = "test_update_id"
    original_config = {"port": 1234, "host": "oldhost", "password": "oldpass", "countries": ["US"]}
    new_port = 5678
    new_host = "newhost"

    # Mock load_config to return the original config
    # Mock save_config to check the updated data
    with patch.object(isolated_config_manager, 'load_config', return_value=original_config) as mock_load, \
         patch.object(isolated_config_manager, 'save_config') as mock_save:
        result = runner.invoke(app, [
            "instance", "update", "--id", instance_id,
            "--port", str(new_port), "--host", new_host
            # Password not provided, so it should remain "oldpass"
        ])

    assert result.exit_code == 0, result.stdout
    assert f"Configuration for instance '{instance_id}' updated successfully." in result.stdout
    
    mock_load.assert_called_with(instance_id)
    
    mock_save.assert_called_once()
    saved_args = mock_save.call_args[0]
    assert saved_args[0] == instance_id       # instance_id
    updated_data = saved_args[1]              # config_data
    assert updated_data["port"] == new_port
    assert updated_data["host"] == new_host
    assert updated_data["password"] == "oldpass" # Should not change
    assert updated_data["countries"] == ["US"]   # Should not change

def test_instance_update_clear_countries(isolated_config_manager: ConfigManager):
    instance_id = "test_update_countries"
    original_config = {"port": 1234, "countries": ["US", "GB"]}
    with patch.object(isolated_config_manager, 'load_config', return_value=original_config), \
         patch.object(isolated_config_manager, 'save_config') as mock_save:
        result = runner.invoke(app, ["instance", "update", "--id", instance_id, "--countries", ""]) # Empty string to clear

    assert result.exit_code == 0, result.stdout
    mock_save.assert_called_once()
    updated_data = mock_save.call_args[0][1]
    assert updated_data["countries"] == []


# --- Tests for `--instance-id` in existing commands ---

@patch('xtor.cli.Tor.startTor') # Mock at the source where it's used by CLI
def test_start_with_instance_id(mock_start_tor, isolated_config_manager: ConfigManager, tmp_path):
    """Test `xtor start --instance-id test_id`."""
    instance_id = "start_inst_id"
    mock_config = DEFAULT_TEST_PARAMS.copy()
    mock_config["port"] = 9999 # Unique port for this test
    
    # Configure the patched config_manager to return this mock_config
    isolated_config_manager.save_config(instance_id, mock_config)

    # Mock the Popen object returned by startTor to have a pid
    mock_popen_instance = MagicMock()
    mock_popen_instance.pid = 12345
    mock_start_tor.return_value = MagicMock(tor=mock_popen_instance, host="mockhost", port=mock_config["port"], control_port=mock_config["control_port"])

    # Use a context manager for patching typer.pause to simulate immediate exit
    with patch('xtor.cli.typer.pause', side_effect=lambda _: None):
        result = runner.invoke(app, ["start", "--instance-id", instance_id])

    assert result.exit_code == 0, result.stdout
    assert f"Starting Tor using parameters from: instance config '{instance_id}'" in result.stdout
    
    # Check Tor.startTor was called with correct parameters from config
    expected_call_params = {
        "port": mock_config["port"],
        "control_port": mock_config["control_port"],
        "host": mock_config["host"],
        "password": mock_config["password"],
        "client_options": mock_config["client_options"],
        "config": mock_config["torrc_config"], # This is torrc_config
        "path": mock_config["path"],
        "own": mock_config["own"],
        "max_circuit_dirtiness": mock_config["max_circuit_dirtiness"],
        "countries": mock_config["countries"]
    }
    mock_start_tor.assert_called_once_with(**expected_call_params)
    
    # Check PID file creation: <instance_id>.pid
    # Home dir is patched by isolate_config_manager_for_cli fixture
    pid_cache_dir = tmp_path / "cli_test_pid_cache" / "xtor"
    expected_pid_file = pid_cache_dir / f"{instance_id}.pid"
    assert expected_pid_file.exists()
    assert expected_pid_file.read_text() == str(mock_popen_instance.pid)
    
    # Check PID file removal after pause (mocked to immediate exit)
    # The cleanup is part of the start command's own logic after typer.pause
    # This requires the mock_stop within tor_instance to also work correctly.
    # For simplicity, we'll assume tor_instance.stop() cleans up self.tor
    # and check if the file is gone.
    # This part of test might be flaky if not careful about how stop() is mocked or handled.
    # The test currently relies on the actual tor_instance.stop() and file cleanup logic.
    # To make it more robust, Tor.stop could be mocked.
    assert not expected_pid_file.exists(), "PID file should be removed after stopping."


@patch('xtor.cli.Tor.startTor')
def test_start_with_instance_id_and_override(mock_start_tor, isolated_config_manager: ConfigManager, tmp_path):
    """Test `xtor start --instance-id test_id --port 9999`."""
    instance_id = "override_inst_id"
    original_port = 8888
    override_port = 9999
    
    mock_config = DEFAULT_TEST_PARAMS.copy()
    mock_config["port"] = original_port
    isolated_config_manager.save_config(instance_id, mock_config)

    mock_popen_instance = MagicMock(pid=54321)
    mock_start_tor.return_value = MagicMock(tor=mock_popen_instance, host="mockhost", port=override_port, control_port=mock_config["control_port"])

    with patch('xtor.cli.typer.pause', side_effect=lambda _: None):
        result = runner.invoke(app, ["start", "--instance-id", instance_id, "--port", str(override_port)])

    assert result.exit_code == 0, result.stdout
    assert f"Starting Tor using parameters from: instance config '{instance_id}' with CLI overrides" in result.stdout
    
    # Assert Tor.startTor was called with the overridden port
    expected_call_params = {
        "port": override_port, # Overridden
        "control_port": mock_config["control_port"],
        "host": mock_config["host"],
        "password": mock_config["password"],
        "client_options": mock_config["client_options"],
        "config": mock_config["torrc_config"],
        "path": mock_config["path"],
        "own": mock_config["own"],
        "max_circuit_dirtiness": mock_config["max_circuit_dirtiness"],
        "countries": mock_config["countries"]
    }
    mock_start_tor.assert_called_once_with(**expected_call_params)

@patch('xtor.cli.os.kill') # Mock os.kill for the stop command
def test_stop_with_instance_id(mock_os_kill, isolated_config_manager: ConfigManager, tmp_path):
    """Test `xtor stop --instance-id test_id`."""
    instance_id = "stop_inst_id"
    pid_to_kill = 6789
    
    # Home dir is patched by isolate_config_manager_for_cli fixture
    pid_cache_dir = tmp_path / "cli_test_pid_cache" / "xtor"
    pid_file = pid_cache_dir / f"{instance_id}.pid"
    pid_file.write_text(str(pid_to_kill))

    result = runner.invoke(app, ["stop", "--instance-id", instance_id])

    assert result.exit_code == 0, result.stdout
    assert f"Attempting to stop Tor process with PID {pid_to_kill}" in result.stdout
    
    # Check os.kill was called with SIGTERM then potentially SIGKILL (if first didn't "work")
    # For this test, just check the SIGTERM call. A more complex mock might be needed for full sequence.
    mock_os_kill.assert_any_call(pid_to_kill, ANY) # First call is os.kill(pid, 0) to check existence
    # Then os.kill(pid, signal.SIGTERM)
    # The ANY helps if signal numbers are tricky to match across platforms in tests
    # More specific: mock_os_kill.assert_any_call(pid_to_kill, signal.SIGTERM)

    # The stop command attempts to remove the PID file.
    # Depending on mock_os_kill behavior (if it raises ProcessLookupError on first check),
    # the file might be removed.
    # If os.kill(pid,0) succeeds, then SIGTERM, then another os.kill(pid,0) which should fail for cleanup.
    # For this test, we'll assume it gets to the point of trying to stop.
    # A more robust test would mock the sequence of os.kill calls.

@patch('xtor.cli.Tor') # Mock the entire Tor class used by status and new-identity
def test_status_with_instance_id(MockTor, isolated_config_manager: ConfigManager):
    """Test `xtor status --instance-id test_id`."""
    instance_id = "status_inst_id"
    mock_config = DEFAULT_TEST_PARAMS.copy()
    mock_config["password"] = "status_pass" # Ensure it's not None for Tor instantiation
    isolated_config_manager.save_config(instance_id, mock_config)

    # Configure the mock Tor instance returned by Tor(...)
    mock_tor_instance = MockTor.return_value
    mock_tor_instance.ip = "1.2.3.4" # Mock the .ip property

    result = runner.invoke(app, ["status", "--instance-id", instance_id])

    assert result.exit_code == 0, result.stdout
    assert f"Attempting to connect to Tor using parameters from: instance config '{instance_id}'" in result.stdout
    assert "Current Tor IP: 1.2.3.4" in result.stdout
    
    MockTor.assert_called_once_with(
        port=mock_config["port"],
        host=mock_config["host"],
        control_port=mock_config["control_port"],
        password=mock_config["password"] # Ensure password from config is used
    )

@patch('xtor.cli.Tor')
def test_new_identity_with_instance_id_and_override(MockTor, isolated_config_manager: ConfigManager):
    """Test `xtor new-identity --instance-id test_id --port 1234 --wait`."""
    instance_id = "newid_inst_id"
    override_port = 1234
    
    mock_config = DEFAULT_TEST_PARAMS.copy()
    mock_config["port"] = 8888 # Original port in config
    mock_config["password"] = "newid_pass"
    isolated_config_manager.save_config(instance_id, mock_config)

    mock_tor_instance = MockTor.return_value
    mock_tor_instance.ip = "1.1.1.1" # Initial IP
    
    # Simulate IP change after new_identity
    def new_identity_side_effect(wait):
        mock_tor_instance.ip = "2.2.2.2"
    mock_tor_instance.new_identity.side_effect = new_identity_side_effect

    result = runner.invoke(app, [
        "new-identity", "--instance-id", instance_id,
        "--port", str(override_port), "--wait"
    ])

    assert result.exit_code == 0, result.stdout
    assert f"Attempting to connect to Tor for new identity using parameters from: instance config '{instance_id}' with CLI overrides" in result.stdout
    assert "New Tor identity confirmed. New IP: 2.2.2.2" in result.stdout
    
    MockTor.assert_called_once_with(
        port=override_port, # Overridden port
        host=mock_config["host"],
        control_port=mock_config["control_port"],
        password=mock_config["password"]
    )
    mock_tor_instance.new_identity.assert_called_once_with(wait=True)

```
