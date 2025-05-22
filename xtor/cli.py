import typer
from pathlib import Path
import os
import signal
import time # For sleep
import json # For pretty printing in list

from xtor import Tor
from xtor.config_manager import ConfigManager
from typing import Optional, Dict, Any

app = typer.Typer()
config_manager = ConfigManager()

# Create a new Typer app for the 'instance' subcommand
instance_app = typer.Typer(name="instance", help="Manage Tor instance configurations.")
app.add_typer(instance_app)

# Default values for Tor parameters
DEFAULT_PARAMS = {
    "host": "127.0.0.1",
    "port": 9052,
    "control_port": 9053,
    "password": "password",
    "path": "tor",
    "countries": [], # Expects a list
    "max_circuit_dirtiness": 0,
    "own": True,
    "client_options": {},
    "torrc_config": {} # 'config' for startTor is torrc_config
}

def _get_tor_params(
    instance_id: Optional[str],
    config_manager: ConfigManager,
    cli_params: Dict[str, Any],
    default_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolves Tor parameters based on instance_id, CLI overrides, and defaults.
    CLI parameters in cli_params should be None if not provided by the user.
    """
    final_params = default_params.copy()
    params_source_message = "defaults"

    if instance_id:
        loaded_config = config_manager.load_config(instance_id)
        if not loaded_config:
            typer.echo(f"Error: Instance configuration ID '{instance_id}' not found.", err=True)
            raise typer.Exit(code=1)
        
        # Ensure countries is a list if loaded from config
        if "countries" in loaded_config and isinstance(loaded_config["countries"], str):
            loaded_config["countries"] = loaded_config["countries"].split(',') if loaded_config["countries"] else []
            
        final_params.update(loaded_config)
        params_source_message = f"instance config '{instance_id}'"

    # Apply CLI overrides: only if the CLI param value is not None
    overridden_by_cli = False
    for key, value in cli_params.items():
        if value is not None:
            # Special handling for countries string from CLI
            if key == "countries" and isinstance(value, str):
                final_params[key] = value.split(',') if value else []
            elif key == "max_time": # CLI uses max_time, config uses max_circuit_dirtiness
                 final_params["max_circuit_dirtiness"] = value
            else:
                final_params[key] = value
            overridden_by_cli = True

    if instance_id and overridden_by_cli:
        params_source_message += " with CLI overrides"
    elif not instance_id and overridden_by_cli:
        params_source_message = "CLI options"
    
    # Ensure required parameters have values after merging everything
    required_keys = ["port", "control_port", "host"]
    for req_key in required_keys:
        if final_params.get(req_key) is None: # Check final resolved value
            typer.echo(f"Error: Required parameter '{req_key}' is missing.", err=True)
            typer.echo(f"Source of parameters: {params_source_message}")
            raise typer.Exit(code=1)
            
    # Add a message about where the parameters came from for transparency
    final_params["_source_message"] = params_source_message
    return final_params
def create_instance(
    instance_id: str = typer.Option(..., "--id", help="Unique ID for the new instance configuration."),
    port: int = typer.Option(DEFAULT_PARAMS["port"], help="SOCKS port for the Tor instance."),
    host: str = typer.Option(DEFAULT_PARAMS["host"], help="Host for the Tor instance."),
    control_port: int = typer.Option(DEFAULT_PARAMS["control_port"], help="Control port for the Tor instance."),
    password: str = typer.Option(DEFAULT_PARAMS["password"], help="Password for the Tor control port."),
    path: str = typer.Option(DEFAULT_PARAMS["path"], help="Path to the Tor binary."),
    countries: str = typer.Option(",".join(DEFAULT_PARAMS["countries"]), help="Comma-separated list of exit node countries (e.g., US,GB)."),
    max_time: int = typer.Option(DEFAULT_PARAMS["max_circuit_dirtiness"], help="Max circuit dirtiness in seconds (0 for none)."),
    own: bool = typer.Option(DEFAULT_PARAMS["own"], help="Whether xtor should take ownership of the Tor process for this config.")
):
    """Create a new Tor instance configuration and save it."""
    config_data = {
        "port": port,
        "host": host,
        "control_port": control_port,
        "password": password,
        "path": path,
        "countries": countries.split(',') if countries else [], # Store as list
        "max_circuit_dirtiness": max_time, # Store with the correct internal key
        "own": own,
        # Add other relevant fields from Tor.startTor if needed, e.g., client_options, torrc_config
        "client_options": {}, # Default empty dict
        "torrc_config": {}    # Default empty dict
    }
    try:
        config_manager.save_config(instance_id, config_data)
        typer.echo(f"Configuration for instance '{instance_id}' created and saved successfully at {config_manager.get_config_file_path()}.")
    except Exception as e:
        typer.echo(f"Error saving configuration for instance '{instance_id}': {e}", err=True)

@instance_app.command("list")
def list_instances():
    """List all saved Tor instance configurations."""
    configs = config_manager.list_configs()
    if not configs:
        typer.echo("No instance configurations found.")
        return
    
    typer.echo("Available instance configurations:")
    for instance_id, config_data in configs.items():
        # Pretty print the config_data dictionary
        # Convert countries list back to string for display if necessary
        display_config = config_data.copy()
        if "countries" in display_config and isinstance(display_config["countries"], list):
            display_config["countries"] = ",".join(display_config["countries"])
        
        details = json.dumps(display_config, indent=2)
        typer.echo(f"\nInstance ID: {instance_id}")
        typer.echo(details)

@instance_app.command("delete")
def delete_instance(
    instance_id: str = typer.Option(..., "--id", help="ID of the instance configuration to delete.")
):
    """Delete a Tor instance configuration."""
    if config_manager.delete_config(instance_id):
        typer.echo(f"Configuration for instance '{instance_id}' deleted successfully.")
    else:
        typer.echo(f"Configuration for instance '{instance_id}' not found.", err=True)

@instance_app.command("update")
def update_instance(
    instance_id: str = typer.Option(..., "--id", help="ID of the instance configuration to update."),
    port: int = typer.Option(None, help="New SOCKS port for the Tor instance."),
    host: str = typer.Option(None, help="New host for the Tor instance."),
    control_port: int = typer.Option(None, help="New control port for the Tor instance."),
    password: str = typer.Option(None, help="New password for the Tor control port."),
    path: str = typer.Option(None, help="New path to the Tor binary."),
    countries: str = typer.Option(None, help="New comma-separated list of exit node countries."),
    max_time: int = typer.Option(None, help="New max circuit dirtiness in seconds (0 for none)."),
    own: bool = typer.Option(None, help="New ownership status for the Tor process.")
    # client_options and torrc_config updates would require more complex input (e.g. JSON string)
    # For now, keeping it to simpler types.
):
    """Update an existing Tor instance configuration."""
    existing_config = config_manager.load_config(instance_id)
    if not existing_config:
        typer.echo(f"Configuration for instance '{instance_id}' not found.", err=True)
        raise typer.Exit(code=1)

    updated_config = existing_config.copy()

    if port is not None:
        updated_config["port"] = port
    if host is not None:
        updated_config["host"] = host
    if control_port is not None:
        updated_config["control_port"] = control_port
    if password is not None:
        updated_config["password"] = password
    if path is not None:
        updated_config["path"] = path
    if countries is not None: # Handle empty string to clear countries
        updated_config["countries"] = countries.split(',') if countries else []
    if max_time is not None:
        updated_config["max_circuit_dirtiness"] = max_time # Internal key
    if own is not None:
        updated_config["own"] = own
    
    # Note: client_options and torrc_config are not updated via simple CLI flags here.
    # A more robust update might involve loading them as JSON strings or similar.

    try:
        config_manager.save_config(instance_id, updated_config)
        typer.echo(f"Configuration for instance '{instance_id}' updated successfully.")
    except Exception as e:
        typer.echo(f"Error updating configuration for instance '{instance_id}': {e}", err=True)

# Modify the start command to optionally use a saved instance configuration
@app.command()
def start(
    instance_id: str = typer.Option(None, "--instance-id", help="Start Tor using a saved instance configuration ID."),
    port: Optional[int] = typer.Option(None, help="Port to listen on (overrides instance config)."),
    host: Optional[str] = typer.Option(None, help="Host to listen on (overrides instance config)."),
    control_port: Optional[int] = typer.Option(None, help="Port to control Tor (overrides instance config)."),
    password: Optional[str] = typer.Option(None, help="Password to control Tor (overrides instance config)."),
    own: Optional[bool] = typer.Option(None, help="Own Tor process (overrides instance config)."),
    path: Optional[str] = typer.Option(None, help="Path to Tor binary (overrides instance config)."),
    countries: Optional[str] = typer.Option(None, help="Countries for Tor exit nodes, comma separated (overrides instance config)."),
    max_time: Optional[int] = typer.Option(None, help="Max circuit dirtiness in seconds (overrides instance config).")
):
    """Start a Tor server, optionally using a saved configuration ID."""
    
    cli_params = {
        "port": port, "host": host, "control_port": control_port, "password": password,
        "own": own, "path": path, "countries": countries, "max_time": max_time
        # client_options and torrc_config (as 'config') are not exposed as direct CLI flags here
        # but could be part of a saved instance config.
    }
    
    start_params = _get_tor_params(instance_id, config_manager, cli_params, DEFAULT_PARAMS.copy())
    params_source_message = start_params.pop("_source_message", "unknown source")
            
    typer.echo(f"Starting Tor using parameters from: {params_source_message}")

    tor_instance = Tor.startTor(
        port=start_params["port"],
        control_port=start_params["control_port"],
        host=start_params["host"],
        password=start_params["password"],
        client_options=start_params.get("client_options", {}),
        config=start_params.get("torrc_config", {}), # This is 'config' for startTor
        path=start_params["path"],
        own=start_params["own"],
        max_circuit_dirtiness=start_params["max_circuit_dirtiness"],
        countries=start_params["countries"]
    )
    typer.echo(f"Tor started on {tor_instance.host}:{tor_instance.port} (Control: {tor_instance.control_port})")

    pid_file_name_part = instance_id if instance_id else str(start_params["control_port"])
    pid_file = None 
    current_pid = None

    if start_params["own"] and tor_instance.tor and hasattr(tor_instance.tor, 'pid'):
        current_pid = tor_instance.tor.pid
        try:
            pid_dir = Path.home() / ".cache" / "xtor"
            pid_dir.mkdir(parents=True, exist_ok=True)
            pid_file = pid_dir / f"{pid_file_name_part}.pid" 
            with open(pid_file, "w") as f:
                f.write(str(current_pid))
            typer.echo(f"Tor process PID {current_pid} saved to {pid_file}")
        except Exception as e:
            typer.echo(f"Error saving PID: {e}", err=True)

    if start_params["own"]:
        typer.pause("Press any key to stop Tor server. ")
        if tor_instance.tor: 
            typer.echo("Stopping Tor server...")
            tor_instance.stop() 
            typer.echo("Tor server stopped.")
            if pid_file and pid_file.exists() and current_pid is not None:
                try:
                    # Check if PID in file matches before deleting, to avoid deleting a PID file from a newer instance
                    # if the old one crashed and didn't clean up.
                    pid_in_file = int(pid_file.read_text())
                    if pid_in_file == current_pid:
                         pid_file.unlink()
                         typer.echo(f"PID file {pid_file} removed.")
                    else:
                        typer.echo(f"PID file {pid_file} not removed, PID mismatch (expected {current_pid}, found {pid_in_file}).", err=True)
                except Exception as e:
                    typer.echo(f"Error removing PID file {pid_file}: {e}", err=True)

@app.command()
def status(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Use a saved instance configuration ID."),
    port: Optional[int] = typer.Option(None, help="Port of the Tor SOCKS proxy (overrides instance config)."),
    host: Optional[str] = typer.Option(None, help="Host of the Tor SOCKS proxy (overrides instance config)."),
    control_port: Optional[int] = typer.Option(None, help="Port for Tor control (overrides instance config)."),
    password: Optional[str] = typer.Option(None, help="Password for Tor control (overrides instance config)."),
):
    """Get the current external IP address through Tor, optionally using a saved instance configuration."""
    cli_params = {"port": port, "host": host, "control_port": control_port, "password": password}
    conn_params = _get_tor_params(instance_id, config_manager, cli_params, DEFAULT_PARAMS.copy())
    params_source_message = conn_params.pop("_source_message", "unknown source")

    typer.echo(f"Attempting to connect to Tor using parameters from: {params_source_message}")
    try:
        # Tor class for existing connections needs password directly if not None
        tor_conn_args = {
            "port": conn_params["port"],
            "host": conn_params["host"],
            "control_port": conn_params["control_port"],
            "password": conn_params["password"] # This should be the actual password, not None if one is required
        }
        if tor_conn_args["password"] is None: # stem controller requires a password, even if empty
            tor_conn_args["password"] = ""


        tor = Tor(**tor_conn_args)
        with tor:
            typer.echo(f"Current Tor IP: {tor.ip}")
    except Exception as e:
        typer.echo(f"Error connecting to Tor or getting IP: {e}", err=True)

@app.command()
def new_identity(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Use a saved instance configuration ID."),
    port: Optional[int] = typer.Option(None, help="Port of the Tor SOCKS proxy (overrides instance config)."),
    host: Optional[str] = typer.Option(None, help="Host of the Tor SOCKS proxy (overrides instance config)."),
    control_port: Optional[int] = typer.Option(None, help="Port for Tor control (overrides instance config)."),
    password: Optional[str] = typer.Option(None, help="Password for Tor control (overrides instance config)."),
    wait: bool = typer.Option(False, help="Wait for the new identity to be confirmed with a new IP."),
):
    """Request a new identity (new IP address) from Tor, optionally using a saved instance configuration."""
    cli_params = {"port": port, "host": host, "control_port": control_port, "password": password}
    conn_params = _get_tor_params(instance_id, config_manager, cli_params, DEFAULT_PARAMS.copy())
    params_source_message = conn_params.pop("_source_message", "unknown source")

    typer.echo(f"Attempting to connect to Tor for new identity using parameters from: {params_source_message}")
    try:
        tor_conn_args = {
            "port": conn_params["port"],
            "host": conn_params["host"],
            "control_port": conn_params["control_port"],
            "password": conn_params["password"]
        }
        if tor_conn_args["password"] is None:
            tor_conn_args["password"] = ""

        tor = Tor(**tor_conn_args)
        with tor:
            old_ip = tor.ip 
            tor.new_identity(wait=wait)
            if wait:
                new_ip = tor.ip
                if new_ip == old_ip:
                    typer.echo("New identity requested, but IP address did not change. This can happen if Tor is unable to establish a new circuit quickly.")
                else:
                    typer.echo(f"New Tor identity confirmed. New IP: {new_ip}")
            else:
                typer.echo("New Tor identity request sent.")
    except Exception as e:
        typer.echo(f"Error connecting to Tor or requesting new identity: {e}", err=True)

@app.command()
def stop(
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Stop Tor instance by its configuration ID (uses <id>.pid)."),
    control_port: Optional[int] = typer.Option(None, help="Control port of the Tor instance to stop (uses <port>.pid if --instance-id is not given).")
):
    """Stop an xtor-managed Tor process by its instance ID or control port."""
    if instance_id and control_port is not None:
        typer.echo("Error: --instance-id and --control-port are mutually exclusive for identifying the Tor process to stop.", err=True)
        raise typer.Exit(code=1)
    if not instance_id and control_port is None:
        typer.echo("Error: Either --instance-id or --control-port must be provided to identify the Tor process to stop.", err=True)
        raise typer.Exit(code=1)

    pid_dir = Path.home() / ".cache" / "xtor"
    pid_file_name_part = instance_id if instance_id else str(control_port)
    pid_file = pid_dir / f"{pid_file_name_part}.pid"
    
    target_identifier = f"instance ID '{instance_id}'" if instance_id else f"control port '{control_port}'"

    if not pid_file.exists():
        typer.echo(f"No PID file found at {pid_file} for Tor process identified by {target_identifier}.")
        typer.echo("The process may not be running or was not started by xtor's start command with the 'own' flag.")
        return

    try:
        pid_str = pid_file.read_text().strip()
        pid = int(pid_str)
    except ValueError:
        typer.echo(f"Invalid PID found in {pid_file}: {pid_str}", err=True)
        return
    except Exception as e:
        typer.echo(f"Error reading PID file {pid_file}: {e}", err=True)
        return

    typer.echo(f"Attempting to stop Tor process with PID {pid} (from control port {control_port}).")

    try:
        # Check if process exists
        os.kill(pid, 0) 
    except OSError: # This means process does not exist or permission issue
        typer.echo(f"Tor process with PID {pid} not found or not accessible. It might have already been stopped.")
        try:
            pid_file.unlink()
            typer.echo(f"PID file {pid_file} removed.")
        except Exception as e:
            typer.echo(f"Error removing stale PID file {pid_file}: {e}", err=True)
        return

    # Try to terminate gracefully
    try:
        typer.echo(f"Sending SIGTERM to PID {pid}...")
        os.kill(pid, signal.SIGTERM)
        # Wait a bit for graceful shutdown
        for _ in range(5): # Check for 5 seconds
            time.sleep(1)
            os.kill(pid, 0) # Check if process still exists
        # If still running after SIGTERM and waiting
        typer.echo(f"Process {pid} still running after SIGTERM, sending SIGKILL...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(1) # Give SIGKILL a moment
        os.kill(pid, 0) # This should raise OSError now if killed
        # If we reach here, SIGKILL failed to stop it immediately or check is flawed
        typer.echo(f"Sent SIGKILL to PID {pid}. If it's still running, manual intervention may be required.", err=True)

    except ProcessLookupError: # Python 3.5+ for os.kill(pid, 0) if process is gone
        typer.echo(f"Tor process with PID {pid} stopped successfully.")
        try:
            pid_file.unlink()
            typer.echo(f"PID file {pid_file} removed.")
        except Exception as e:
            typer.echo(f"Error removing PID file {pid_file}: {e}", err=True)
    except OSError as e:
        # This will catch os.kill(pid, 0) if process is gone after SIGTERM/SIGKILL
        # or if there was a permission error
        if e.errno == 3: # ESRCH, no such process
             typer.echo(f"Tor process with PID {pid} stopped successfully.")
             try:
                 pid_file.unlink()
                 typer.echo(f"PID file {pid_file} removed.")
             except Exception as unlink_e:
                 typer.echo(f"Error removing PID file {pid_file}: {unlink_e}", err=True)
        elif e.errno == 1: # EPERM, operation not permitted
            typer.echo(f"Permission error trying to stop process {pid}. Try with sudo or as the user who started it.", err=True)
        else: # Other OS errors
            typer.echo(f"An OS error occurred while trying to stop process {pid}: {e}", err=True)

    except Exception as e:
        typer.echo(f"An unexpected error occurred: {e}", err=True)
    

def main():
    app()