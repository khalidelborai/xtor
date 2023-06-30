from subprocess import Popen
from typing import Optional

from httpx import Client
from stem.control import Controller
from stem.process import launch_tor_with_config
from where import first as where

from xtor.utils import checkPort, getTorPassHash


class Tor:
    def __init__(
        self,
        password: str,
        port: int = 9050,
        control_port: int = 9051,
        host: Optional[str] = "127.0.0.1",
        client_options: Optional[dict] = {},
        tor: Optional[Popen] = None,
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
        """
        self.port = port
        self.password = password
        self.control_port = control_port
        self.controller = Controller.from_port(port=self.control_port)
        self.client_options = client_options
        self.tor = tor
        self.host = host

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
        *args,
        **kwargs,
    ) -> "Tor":
        """
        Start Tor

        Args:
            port (int): Port to use for Tor
            control_port (int): Control port to use for Tor
            host (str): Host to use for Tor
            password (Optional[str], optional): Password to use for Tor. Defaults to None.
            client_options (Optional[dict], optional): Client options to use for Tor. Defaults to {}.
            config (Optional[dict], optional): Tor instance additional config
            own (Optional[bool], optional): asserts ownership over the tor process so it aborts if this python process terminates or a `Controller` we establish to it disconnects

        Raises:
            Exception: If port is already in use
            Exception: If control_port is already in use

        Returns:
            Tor: Tor instance
        """

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
        
        config = {
            "SocksPort": str(port),
            "ControlPort": str(control_port),
            **config,
        }

        if password is not None:
            config["HashedControlPassword"] = getTorPassHash(password)

        

        tor: Popen = launch_tor_with_config(
            config=config,
            take_ownership=own,
            *args,
            **kwargs,
        )



        return Tor(
            password=password,
            port=port,
            control_port=control_port,
            client_options=client_options,
            tor=tor,
            host=host,
        )

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