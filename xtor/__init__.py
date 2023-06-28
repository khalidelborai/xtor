__version__ = "0.1.2"

from httpx import Client
from stem.control import Controller

from xtor.utils import checkPort, getTorPassHash


class Tor:
    def __init__(
        self,
        password: str,
        port: int = 9050,
        control_port: int = 9051,
    ) -> None:
        self.port = port

        self.password = password
        self.control_port = control_port
        self.controller = Controller.from_port(port=self.control_port)

    @property
    def client(self) -> Client:
        """
        Get httpx Client
        """
        if not hasattr(self, "_client"):
            self._client = Client(
                proxies=f"socks5://localhost:{self.port}",
            )
        return self._client

    def __connect(self) -> None:
        """
        Connect to Tor
        """
        self.controller.authenticate(password=self.password)

    def __disconnect(self) -> None:
        """
        Disconnect from Tor
        """
        self.controller.close()

    def __enter__(self) -> "Tor":
        """
        Enter context manager
        """
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit context manager
        """
        self.__disconnect()

    def __getIP(self) -> str:
        """
        Get IP
        """
        return self.client.get("http://api.ipify.org").text

    @property
    def ip(self) -> str:
        """
        Get IP
        """
        return self.__getIP()
