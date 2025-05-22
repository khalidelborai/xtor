import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from xtor.config_manager import ConfigManager

@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Creates a temporary configuration directory for tests."""
    return tmp_path / ".config" / "xtor"

@pytest.fixture
def manager(temp_config_dir: Path) -> ConfigManager:
    """Returns a ConfigManager instance using the temporary config directory."""
    # We pass the temp_config_dir to the ConfigManager constructor
    return ConfigManager(config_dir=temp_config_dir)

def test_init_no_existing_file(manager: ConfigManager, temp_config_dir: Path):
    """Check that ConfigManager initializes with an empty configs dict if no instances.json exists."""
    assert manager.configs == {}
    assert not (temp_config_dir / "instances.json").exists() # Initially, it shouldn't exist until a save.
    # The __init__ itself creates the directory, let's check that
    assert temp_config_dir.exists()
    assert temp_config_dir.is_dir()

def test_init_with_existing_file(temp_config_dir: Path):
    """Mock an instances.json with some data and check that ConfigManager loads it correctly."""
    config_data = {
        "test_id1": {"port": 9050, "host": "localhost"},
        "test_id2": {"port": 9060, "host": "127.0.0.1"}
    }
    # Ensure the directory exists before creating the file in it
    temp_config_dir.mkdir(parents=True, exist_ok=True)
    config_file = temp_config_dir / "instances.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    manager = ConfigManager(config_dir=temp_config_dir) # Initialize AFTER file is created
    assert manager.configs == config_data

def test_init_with_corrupt_file(temp_config_dir: Path, capsys):
    """Mock a corrupt instances.json and check that ConfigManager handles it gracefully."""
    temp_config_dir.mkdir(parents=True, exist_ok=True)
    config_file = temp_config_dir / "instances.json"
    with open(config_file, "w") as f:
        f.write("this is not json")

    manager = ConfigManager(config_dir=temp_config_dir)
    assert manager.configs == {} # Should default to empty
    captured = capsys.readouterr()
    assert f"Error decoding JSON from {config_file}" in captured.out # Check for error print

def test_init_directory_creation_error(tmp_path: Path, capsys):
    """Test graceful handling of directory creation error."""
    # Create a file where the directory should be, to cause mkdir to fail
    bad_path_base = tmp_path / "file_instead_of_dir_base"
    bad_config_dir = bad_path_base / ".config" / "xtor"
    bad_path_base.mkdir() # Create the base
    (bad_path_base / ".config").write_text("I am a file") # Create a file where .config dir should be

    manager = ConfigManager(config_dir=bad_config_dir)
    captured = capsys.readouterr()
    assert f"Error creating config directory {bad_config_dir}" in captured.out
    assert manager.configs == {} # Should still initialize to empty

def test_save_config(manager: ConfigManager, temp_config_dir: Path):
    """Save a new config, check that it's in self.configs and that the file is written."""
    instance_id = "new_config"
    config_data = {"port": 9070, "host": "test_host"}
    
    manager.save_config(instance_id, config_data)
    
    assert instance_id in manager.configs
    assert manager.configs[instance_id] == config_data
    
    # Check if file was actually written
    config_file = temp_config_dir / "instances.json"
    assert config_file.exists()
    with open(config_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data[instance_id] == config_data

def test_save_config_value_errors(manager: ConfigManager):
    """Test that save_config raises ValueError for invalid input types."""
    with pytest.raises(ValueError, match="instance_id must be a string"):
        manager.save_config(123, {"port": 9050}) # type: ignore
    with pytest.raises(ValueError, match="config_data must be a dictionary"):
        manager.save_config("test_id", "not_a_dict") # type: ignore


def test_load_config(manager: ConfigManager):
    """Save a config, then load it, check if data matches. Test loading non-existent ID."""
    instance_id = "load_test"
    config_data = {"port": 9080, "option": "value"}
    
    manager.save_config(instance_id, config_data)
    
    loaded_data = manager.load_config(instance_id)
    assert loaded_data == config_data
    
    non_existent_data = manager.load_config("does_not_exist")
    assert non_existent_data is None

def test_delete_config(manager: ConfigManager, temp_config_dir: Path):
    """Save a config, delete it, check it's gone and file is updated. Test deleting non-existent ID."""
    instance_id = "delete_test"
    config_data = {"port": 9090}
    
    manager.save_config(instance_id, config_data) # Save to create the file initially
    assert instance_id in manager.configs
    
    # Delete existing
    deleted = manager.delete_config(instance_id)
    assert deleted is True
    assert instance_id not in manager.configs
    
    # Check file content
    config_file = temp_config_dir / "instances.json"
    with open(config_file, "r") as f:
        saved_data = json.load(f)
    assert instance_id not in saved_data
    
    # Delete non-existent
    deleted_non_existent = manager.delete_config("does_not_exist")
    assert deleted_non_existent is False

def test_list_configs(manager: ConfigManager):
    """Save multiple configs, check if list_configs returns them."""
    config1 = {"id": "id1", "data": {"port": 1111}}
    config2 = {"id": "id2", "data": {"port": 2222}}
    
    manager.save_config(config1["id"], config1["data"])
    manager.save_config(config2["id"], config2["data"])
    
    listed_configs = manager.list_configs()
    assert len(listed_configs) == 2
    assert listed_configs[config1["id"]] == config1["data"]
    assert listed_configs[config2["id"]] == config2["data"]
    
    # Ensure it's a copy
    listed_configs["new_fake_id"] = {"port": 3333}
    assert "new_fake_id" not in manager.configs

def test_get_config_file_path(manager: ConfigManager, temp_config_dir: Path):
    """Test the get_config_file_path method."""
    expected_path = (temp_config_dir / "instances.json").resolve()
    assert Path(manager.get_config_file_path()) == expected_path

# Example of how to mock _save_all_configs_to_file if direct file check is not desired for some tests
def test_save_config_mocked_save_file(manager: ConfigManager):
    with patch.object(manager, '_save_all_configs_to_file') as mock_save_method:
        manager.save_config("mock_test", {"port": 1234})
        mock_save_method.assert_called_once()

def test_delete_config_mocked_save_file(manager: ConfigManager):
    manager.save_config("delete_mock_test", {"port": 5678}) # Ensure it exists
    with patch.object(manager, '_save_all_configs_to_file') as mock_save_method:
        manager.delete_config("delete_mock_test")
        mock_save_method.assert_called_once()
    
    # Test deleting non-existent config does not call save
    with patch.object(manager, '_save_all_configs_to_file') as mock_save_method_non_existent:
        manager.delete_config("non_existent_for_mock")
        mock_save_method_non_existent.assert_not_called()

# TODO: Consider testing _load_all_configs_from_file and _save_all_configs_to_file for permission errors
# This would require more complex mocking of Path.open or file system permissions.
# For now, the existing tests cover file not found, corrupt JSON, and basic success cases.
# The init test for directory creation error also covers a form of permission/OS error.

# Test for _load_all_configs_from_file general exception
def test_load_all_configs_general_exception(temp_config_dir: Path, capsys):
    manager = ConfigManager(config_dir=temp_config_dir) # Manager to work with
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = Exception("Unexpected IO error")
        loaded_configs = manager._load_all_configs_from_file() # Call directly for this specific test
        assert loaded_configs == {}
        captured = capsys.readouterr()
        assert "An unexpected error occurred while loading" in captured.out

# Test for _save_all_configs_to_file general exception
def test_save_all_configs_general_exception(manager: ConfigManager, capsys):
    manager.save_config("test", {"data": "value"}) # Add some data
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = Exception("Unexpected IO error during save")
        manager._save_all_configs_to_file() # Call directly
        captured = capsys.readouterr()
        assert "Error saving configs to" in captured.out
        # Note: In a real scenario, self.configs would still hold the data in memory.
        # The test verifies that the error during save is caught and reported.
```
