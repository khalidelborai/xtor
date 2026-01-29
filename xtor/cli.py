"""xtor CLI - Manage Tor instances."""

from __future__ import annotations

from pathlib import Path

import typer

from xtor.exceptions import XtorError
from xtor.state import (
    InstanceState,
    get_instance,
    list_instances,
    remove_instance,
    remove_instance_data_dir,
)
from xtor.tor import Tor

app = typer.Typer(help="Manage Tor instances")


def check_process_running(pid: int | None) -> bool:
    """Check if a process with given PID is running."""
    if pid is None:
        return False
    try:
        import os
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


@app.command()
def start(
    name: str = typer.Argument(..., help="Name for the instance"),
    port: int = typer.Option(9052, help="SOCKS port"),
    control_port: int = typer.Option(9053, "--control-port", help="Control port"),
    host: str = typer.Option("127.0.0.1", help="Host address"),
    password: str | None = typer.Option(None, help="Password (auto-generated if not provided)"),
    countries: str | None = typer.Option(None, help="Exit countries, comma-separated (e.g., US,DE)"),
    path: Path | None = typer.Option(None, help="Path to tor binary"),
    max_time: int = typer.Option(0, "--max-time", help="MaxCircuitDirtiness in seconds"),
) -> None:
    """Start a named Tor instance."""
    # Check if instance already exists
    existing = get_instance(name)
    if existing and check_process_running(existing.pid):
        typer.echo(f"Instance '{name}' is already running (PID: {existing.pid})")
        raise typer.Exit(code=1)

    country_list = countries.split(",") if countries else None

    try:
        tor = Tor.start(
            port=port,
            control_port=control_port,
            host=host,
            password=password,
            countries=country_list,
            path=str(path) if path else None,
            max_circuit_dirtiness=max_time if max_time > 0 else None,
            own=False,  # Background process
            name=name,
        )

        typer.echo(f"Instance '{name}' started successfully.")
        typer.echo(f"  SOCKS Port: {tor.port}")
        typer.echo(f"  Control Port: {tor.control_port}")
        typer.echo(f"  Password: {tor.password}")
        typer.echo(f"  Host: {tor.host}")

    except XtorError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def stop(
    name: str = typer.Argument(..., help="Name of instance to stop"),
) -> None:
    """Stop a named Tor instance."""
    instance = get_instance(name)
    if instance is None:
        typer.echo(f"Instance '{name}' not found.")
        raise typer.Exit(code=1)

    if instance.pid and check_process_running(instance.pid):
        try:
            import os
            import signal
            os.kill(instance.pid, signal.SIGTERM)
            typer.echo(f"Instance '{name}' stopped (PID: {instance.pid})")
        except OSError as e:
            typer.echo(f"Error stopping instance: {e}", err=True)
    else:
        typer.echo(f"Instance '{name}' was not running.")

    remove_instance(name)


@app.command()
def remove(
    name: str = typer.Argument(..., help="Name of instance to remove"),
) -> None:
    """Stop and remove a named Tor instance completely."""
    instance = get_instance(name)
    if instance is None:
        typer.echo(f"Instance '{name}' not found.")
        raise typer.Exit(code=1)

    # Stop first
    if instance.pid and check_process_running(instance.pid):
        try:
            import os
            import signal
            os.kill(instance.pid, signal.SIGTERM)
            typer.echo(f"Instance '{name}' stopped.")
        except OSError:
            pass

    # Remove state and data
    remove_instance(name)
    if remove_instance_data_dir(name):
        typer.echo(f"Data directory for '{name}' removed.")

    typer.echo(f"Instance '{name}' removed.")


@app.command(name="list")
def list_cmd() -> None:
    """List all managed Tor instances."""
    instances = list_instances()

    if not instances:
        typer.echo("No managed instances found.")
        return

    typer.echo("Managed Tor Instances:")
    typer.echo("-" * 60)

    for inst in instances:
        running = check_process_running(inst.pid)
        status = typer.style("running", fg=typer.colors.GREEN) if running else typer.style("stopped", fg=typer.colors.RED)

        typer.echo(f"  {inst.name}")
        typer.echo(f"    Status: {status}")
        typer.echo(f"    SOCKS:  {inst.host}:{inst.port}")
        typer.echo(f"    Control: {inst.host}:{inst.control_port}")
        if inst.pid:
            typer.echo(f"    PID: {inst.pid}")
        typer.echo()


@app.command()
def connect(
    name: str = typer.Argument(..., help="Name of instance"),
) -> None:
    """Show connection details for a named instance."""
    instance = get_instance(name)
    if instance is None:
        typer.echo(f"Instance '{name}' not found.")
        raise typer.Exit(code=1)

    running = check_process_running(instance.pid)
    status = "running" if running else "stopped"

    typer.echo(f"Connection details for '{name}' ({status}):")
    typer.echo(f"  Host: {instance.host}")
    typer.echo(f"  SOCKS Port: {instance.port}")
    typer.echo(f"  Control Port: {instance.control_port}")
    typer.echo(f"  Password: {instance.password}")

    if running:
        typer.echo()
        typer.echo("Python usage:")
        typer.echo(f'  from xtor import Tor')
        typer.echo(f'  tor = Tor.from_name("{name}")')
        typer.echo(f'  with tor:')
        typer.echo(f'      print(tor.ip)')


def main() -> None:
    """CLI entry point."""
    app()
