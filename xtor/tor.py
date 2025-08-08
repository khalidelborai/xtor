import secrets
import string
from subprocess import Popen
from typing import Optional

from httpx import Client
from stem.control import Controller
from stem.process import launch_tor_with_config
from where import first as where

from xtor.state import (
    create_instance_dir,
    read_state,
    remove_instance_dir,
    write_state,
)
from xtor.utils import checkPort, getTorPassHash


def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


class Tor:
    def __init__(
        self,
        password: str,
        port: int = 9050,
        control_port: int = 9051,
        host: Optional[str] = "127.0.0.1",
        client_options: Optional[dict] = {},
        tor: Optional[Popen] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Tor instance

        Args:
            password (str): Password to use for Tor
            port (int, optional): Port to use for Tor. Defaults to 9050.
            control_port (int, optional): Control port to use for Tor. Defaults to 9051.
            host (Optional[str], optional): Host to use for Tor. Defaults to "
            client_options (Optional[dict], optional): Client options to use for Tor. Defaults to {}.
            tor (Optional[Popen], optional): Tor process. Defaults to None.
            name (Optional[str], optional): Name of the instance. Defaults to None.
        """
        self.port = port
        self.password = password
        self.control_port = control_port
        self.controller = Controller.from_port(port=self.control_port)
        self.client_options = client_options
        self.tor = tor
        self.host = host
        self.name = name

    @classmethod
    def create(
        cls,
        port: int,
        control_port: int,
        host: str,
        password: Optional[str] = None,
        client_options: Optional[dict] = {},
        config: Optional[dict] = {},
        path: Optional[str] = None,
        own: Optional[bool] = True,
        max_circuit_dirtiness: Optional[int] = None,
        countries: Optional[list] = None,
        name: Optional[str] = None,
        *args,
        **kwargs,
    ) -> "Tor":
        if path is not None:
            kwargs["tor_cmd"] = path
        if path is None:
            if where("tor") is None:
                raise Exception("Tor is not installed")
            kwargs["tor_cmd"] = where("tor")

        if not checkPort(port, host):
            raise Exception(f"Port {port} is already in use")
        if not checkPort(control_port, host):
            raise Exception(f"Port {control_port} is already in use")

        if password is None:
            password = generate_password()

        tor_config = {
            "SocksPort": str(port),
            "ControlPort": str(control_port),
            "HashedControlPassword": getTorPassHash(password),
            **config,
        }

        if max_circuit_dirtiness is not None and max_circuit_dirtiness >= 10:
            tor_config["MaxCircuitDirtiness"] = str(max_circuit_dirtiness)
        if countries is not None:
            tor_config["ExitNodes"] = "{" + ",".join(countries) + "}"

        if name:
            instance_dir = create_instance_dir(name)
            tor_config["DataDirectory"] = str(instance_dir)

        tor_process = launch_tor_with_config(
            config=tor_config,
            take_ownership=own,
            *args,
            **kwargs,
        )

        instance = cls(
            password=password,
            port=port,
            control_port=control_port,
            client_options=client_options,
            tor=tor_process,
            host=host,
            name=name,
        )

        if name:
            state = read_state()
            state[name] = {
                "pid": tor_process.pid,
                "port": port,
                "control_port": control_port,
                "password": password,
                "host": host,
                "data_dir": str(instance_dir),
            }
            write_state(state)

        return instance

    @staticmethod
    def startTor(
        port: int,
        control_port: int,
        host: str,
        password: Optional[str] = None,
        client_options: Optional[dict] = {},
        config: Optional[dict] = {},
        path: Optional[str] = None,
        own: Optional[bool] = True,
        max_circuit_dirtiness: Optional[int] = None,
        countries: Optional[list] = None,
        *args,
        **kwargs,
    ) -> "Tor":
        return Tor.create(
            port=port,
            control_port=control_port,
            host=host,
            password=password,
            client_options=client_options,
            config=config,
            path=path,
            own=own,
            max_circuit_dirtiness=max_circuit_dirtiness,
            countries=countries,
            *args,
            **kwargs,
        )

    @classmethod
    def from_name(cls, name: str) -> "Tor":
        state = read_state()
        if name not in state:
            raise Exception(f"Instance '{name}' not found.")

        instance_data = state[name]
        return cls(
            password=instance_data["password"],
            port=instance_data["port"],
            control_port=instance_data["control_port"],
            host=instance_data["host"],
            name=name,
        )

    def stop(self):
        if self.name:
            state = read_state()
            if self.name in state:
                pid = state[self.name].get("pid")
                if pid:
                    try:
                        import psutil
                        process = psutil.Process(pid)
                        process.terminate()
                        process.wait(timeout=5)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass  # Process already gone or not accessible or timed out
                del state[self.name]
                write_state(state)
        elif self.tor:
            self.tor.terminate()

    @property
    def client(self) -> Client:
        """
        Get httpx Client

        Returns:
            Client: httpx Client

        """
        if not hasattr(self, "_client"):
            self._client = Client(
                **self.client_options,
                proxies=f"socks5://{self.host}:{self.port}",
                timeout=None,
            )
        return self._client

    def connect(self) -> None:
        """
        Connect to Tor
        """
        self.controller.authenticate(password=self.password)

    def disconnect(self) -> None:
        """
        Disconnect from Tor
        """
        self.controller.close()

    def __enter__(self) -> "Tor":
        """
        Enter context manager
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit context manager
        """
        self.disconnect()

    def __getIP(self) -> str:
        """
        Get IP
        """
        return self.client.get("http://api.ipify.org").text

    @property
    def ip(self) -> str:
        """
        Get connected instance IP

        Returns:
            str: instance IP

        """
        if not hasattr(self, "_ip"):
            self._ip = self.__getIP()
        return self._ip
    
    def new_identity(self, wait = False) -> None:
        """
        Get new identity
        """
        self.controller.signal("NEWNYM")
        ip = self.__getIP()
        if wait:
            while ip == self.ip:
                ip = self.__getIP()
        self._ip = ip
        

    def kill(self) -> None:
        """
        Kill Tor process
        """
        self.tor.kill()

    def terminate(self) -> None:
        """
        Terminate Tor process
        """
        self.tor.terminate()