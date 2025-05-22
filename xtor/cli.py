import typer
from pathlib import Path
import os
import signal
import time # For sleep

from xtor import Tor

app = typer.Typer()

@app.command()
def start(
    port: int = typer.Option(9052, help="Port to listen on"),
    host: str = typer.Option("127.0.0.1", help="Host to listen on"),
    control_port: int = typer.Option(9053, help="Port to control tor"),
    password: str = typer.Option("password", help="Password to control tor"),
    own: bool = typer.Option(True, help="Own tor process"),
    path: str = typer.Option("tor", help="Path to tor binary"),
    countries: str = typer.Option('EG,DE', help="Countries to use for tor, comma separated"),
    max_time: int = typer.Option(0, help="Max time to run tor"),
):
    """Start a tor server"""
    tor_instance = Tor.startTor(port=port, host=host, control_port=control_port, password=password, own=own, path=path, countries=countries.split(','),max_circuit_dirtiness=max_time)
    typer.echo(f"Tor started on {tor_instance.host}:{tor_instance.port}")

    if own and tor_instance.tor and hasattr(tor_instance.tor, 'pid'):
        pid = tor_instance.tor.pid
        try:
            pid_dir = Path.home() / ".cache" / "xtor"
            pid_dir.mkdir(parents=True, exist_ok=True)
            pid_file = pid_dir / f"{control_port}.pid"
            with open(pid_file, "w") as f:
                f.write(str(pid))
            typer.echo(f"Tor process PID {pid} saved to {pid_file}")
        except Exception as e:
            typer.echo(f"Error saving PID: {e}", err=True)

    if own:
        typer.pause("Press any key to stop tor server. ")
        # When pause is finished, if tor_instance was started by this command, stop it.
        if tor_instance.tor:
            typer.echo("Stopping Tor server...")
            tor_instance.stop() # This uses the Popen object's methods
            typer.echo("Tor server stopped.")
            # Clean up PID file if it was this instance that created it
            if hasattr(tor_instance.tor, 'pid') and pid_file.exists() : # check pid_file was defined
                try:
                    pid_in_file = int(pid_file.read_text())
                    if pid_in_file == pid: # check if pid in file is the same as the one we started
                         pid_file.unlink()
                         typer.echo(f"PID file {pid_file} removed.")
                except Exception as e:
                    typer.echo(f"Error removing PID file {pid_file}: {e}", err=True)

@app.command()
def status(
    port: int = typer.Option(9052, help="Port of the Tor SOCKS proxy"),
    host: str = typer.Option("127.0.0.1", help="Host of the Tor SOCKS proxy"),
    control_port: int = typer.Option(9053, help="Port for Tor control"),
    password: str = typer.Option("password", help="Password for Tor control"),
):
    """Get the current external IP address through Tor."""
    try:
        tor = Tor(
            port=port,
            host=host,
            control_port=control_port,
            password=password,
        )
        with tor:
            typer.echo(f"Current Tor IP: {tor.ip}")
    except Exception as e:
        typer.echo(f"Error connecting to Tor or getting IP: {e}", err=True)

@app.command()
def new_identity(
    port: int = typer.Option(9052, help="Port of the Tor SOCKS proxy"),
    host: str = typer.Option("127.0.0.1", help="Host of the Tor SOCKS proxy"),
    control_port: int = typer.Option(9053, help="Port for Tor control"),
    password: str = typer.Option("password", help="Password for Tor control"),
    wait: bool = typer.Option(False, help="Wait for the new identity to be confirmed with a new IP."),
):
    """Request a new identity (new IP address) from Tor."""
    try:
        tor = Tor(
            port=port,
            host=host,
            control_port=control_port,
            password=password,
        )
        with tor:
            old_ip = tor.ip # Get current IP to compare if wait is True
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
    control_port: int = typer.Option(9053, help="Control port of the Tor instance to stop"),
    # password: str = typer.Option("password", help="Password for the Tor control port (currently not used for stopping via PID)"),
):
    """Stop an xtor-managed Tor process by its control port."""
    pid_dir = Path.home() / ".cache" / "xtor"
    pid_file = pid_dir / f"{control_port}.pid"

    if not pid_file.exists():
        typer.echo(f"No PID file found at {pid_file}. Tor process for control port {control_port} may not be running or was not started by xtor's start command.")
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