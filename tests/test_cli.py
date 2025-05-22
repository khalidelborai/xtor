from typer.testing import CliRunner
from xtor.cli import app # Assuming your Typer app is named 'app' in xtor/cli.py

runner = CliRunner()

def test_start_command_help():
    """Test the --help option for the 'start' command."""
    result = runner.invoke(app, ["start", "--help"])
    assert result.exit_code == 0
    assert "Start a tor server" in result.stdout
    assert "--port" in result.stdout
    assert "--control-port" in result.stdout

def test_status_command_help():
    """Test the --help option for the 'status' command."""
    result = runner.invoke(app, ["status", "--help"])
    assert result.exit_code == 0
    assert "Get the current external IP address through Tor." in result.stdout
    assert "--port" in result.stdout
    assert "--control-port" in result.stdout

def test_new_identity_command_help():
    """Test the --help option for the 'new-identity' command."""
    result = runner.invoke(app, ["new-identity", "--help"])
    assert result.exit_code == 0
    assert "Request a new identity (new IP address) from Tor." in result.stdout
    assert "--wait" in result.stdout

def test_stop_command_help():
    """Test the --help option for the 'stop' command."""
    result = runner.invoke(app, ["stop", "--help"])
    assert result.exit_code == 0
    assert "Stop an xtor-managed Tor process by its control port." in result.stdout
    assert "--control-port" in result.stdout

# Future considerations noted:
# - Mocking xtor.tor.Tor class methods.
# - Using ephemeral ports for testing actual start and stop.
# - Testing PID file creation and deletion.
# - Testing actual IP changes (mocked) for new-identity.
