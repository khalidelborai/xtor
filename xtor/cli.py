import typer

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
    tor = Tor.startTor(port=port, host=host, control_port=control_port, password=password, own=own, path=path, countries=countries,max_circuit_dirtiness=max_time)
    typer.echo(f"Tor started on {tor.host}:{tor.port}")

    if own:
        typer.pause(
            "Press any key to stop tor server. "
        )
    

def main():
    app()