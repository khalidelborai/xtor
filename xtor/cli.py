import typer
from typing import Optional
import psutil

from xtor import Tor
from xtor.state import read_state, remove_instance_dir, write_state
from xtor.utils import checkPort

app = typer.Typer()


@app.command()
def start(
    name: str = typer.Argument(..., help="Name of the instance to start"),
    port: int = typer.Option(9052, help="SOCKS port for Tor"),
    control_port: int = typer.Option(9053, help="Control port for Tor"),
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    password: Optional[str] = typer.Option(None, help="Password for the control port (will be generated if not provided)"),
    countries: Optional[str] = typer.Option(None, help="Comma-separated list of exit node countries"),
    max_circuit_dirtiness: int = typer.Option(10, help="Max circuit dirtiness time in seconds"),
    path: Optional[str] = typer.Option(None, help="Path to the Tor binary"),
):
    """Starts a new managed Tor instance."""
    state = read_state()
    if name in state:
        typer.echo(f"Instance '{name}' already exists. Use 'xtor stop {name}' and 'xtor remove {name}' to remove it first.")
        raise typer.Exit(code=1)

    country_list = countries.split(',') if countries else None

    try:
        instance = Tor.create(
            port=port,
            control_port=control_port,
            host=host,
            password=password,
            name=name,
            countries=country_list,
            max_circuit_dirtiness=max_circuit_dirtiness,
            path=path,
            own=False,  # Managed instances should run in the background
        )
        typer.echo(f"Instance '{name}' started successfully.")
        typer.echo(f"SOCKS Port: {instance.port}")
        typer.echo(f"Control Port: {instance.control_port}")
        typer.echo(f"Password: {instance.password}")
    except Exception as e:
        typer.echo(f"Error starting instance '{name}': {e}")
        remove_instance_dir(name) # Clean up created directory
        raise typer.Exit(code=1)


@app.command()
def stop(name: str = typer.Argument(..., help="Name of the instance to stop")):
    """Stops a managed Tor instance."""
    state = read_state()
    if name not in state:
        typer.echo(f"Instance '{name}' not found.")
        raise typer.Exit(code=1)

    try:
        instance_data = state[name]
        pid = instance_data.get("pid")
        if pid and psutil.pid_exists(pid):
            p = psutil.Process(pid)
            p.terminate()
            typer.echo(f"Instance '{name}' stopped.")
        else:
            typer.echo(f"Instance '{name}' was not running.")

        del state[name]
        write_state(state)
    except Exception as e:
        typer.echo(f"Error stopping instance '{name}': {e}")
        raise typer.Exit(code=1)


@app.command(name="list")
def list_instances():
    """Lists all managed Tor instances and their status."""
    state = read_state()
    if not state:
        typer.echo("No managed instances found.")
        return

    typer.echo("Managed Tor Instances:")
    for name, data in state.items():
        host = data.get('host', '127.0.0.1')
        port = data.get('port')
        pid = data.get('pid')

        status = typer.style("stopped", fg=typer.colors.RED)
        if pid and psutil.pid_exists(pid):
             # A more reliable check could be trying to connect to the control port
            if not checkPort(port, host):
                 status = typer.style("running", fg=typer.colors.GREEN)

        typer.echo(f"- {name}: {status} (SOCKS: {host}:{port}, PID: {pid or 'N/A'})")


@app.command()
def remove(name: str = typer.Argument(..., help="Name of the instance to remove")):
    """Stops and removes a managed Tor instance."""
    stop(name) # First, ensure it's stopped and removed from state
    try:
        remove_instance_dir(name)
        typer.echo(f"Data directory for instance '{name}' removed.")
    except Exception as e:
        typer.echo(f"Error removing data directory for instance '{name}': {e}")
        raise typer.Exit(code=1)


@app.command()
def connect(name: str = typer.Argument(..., help="Name of the instance to get connection details for")):
    """Gets connection details for a managed Tor instance."""
    state = read_state()
    if name not in state:
        typer.echo(f"Instance '{name}' not found.")
        raise typer.Exit(code=1)

    data = state[name]
    typer.echo(f"Connection details for instance '{name}':")
    typer.echo(f"  Host: {data['host']}")
    typer.echo(f"  SOCKS Port: {data['port']}")
    typer.echo(f"  Control Port: {data['control_port']}")
    typer.echo(f"  Password: {data['password']}")


def main():
    app()