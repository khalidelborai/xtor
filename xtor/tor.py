import time
from subprocess import Popen
from typing import Optional

from httpx import Client
from stem.control import Controller
from stem.process import launch_tor_with_config
from where import first as where

from xtor.utils import checkPort, getTorPassHash
from xtor.config_manager import ConfigManager # Added import


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
    def from_config_id(cls, instance_id: str, config_manager: ConfigManager) -> "Tor":
        """
        Creates and starts a Tor instance from a saved configuration ID.

        Args:
            instance_id (str): The unique identifier for the Tor instance configuration.
            config_manager (ConfigManager): The configuration manager instance to use
                                            for loading the configuration.

        Returns:
            Tor: The started Tor instance.

        Raises:
            ValueError: If the instance configuration with the given ID is not found.
        """
        config_data = config_manager.load_config(instance_id)
        if config_data is None:
            raise ValueError(f"Instance configuration with ID '{instance_id}' not found.")

        # Extract parameters, providing defaults that align with startTor or common usage
        # Required parameters for startTor that must be in config or have sensible global defaults
        port = config_data.get("port")
        control_port = config_data.get("control_port")
        host = config_data.get("host", "127.0.0.1") # Default from Tor.__init__

        if port is None:
            raise ValueError(f"Missing 'port' in configuration for instance ID '{instance_id}'.")
        if control_port is None:
            raise ValueError(f"Missing 'control_port' in configuration for instance ID '{instance_id}'.")

        # Optional parameters for startTor
        password = config_data.get("password") # Defaults to None if not present
        client_options = config_data.get("client_options", {})
        # 'config' here refers to torrc_config for launch_tor_with_config
        torrc_config = config_data.get("torrc_config", {}) # formerly 'config' in startTor signature
        path = config_data.get("path")
        own = config_data.get("own", True) # Default from startTor
        max_circuit_dirtiness = config_data.get("max_circuit_dirtiness")
        countries = config_data.get("countries")
        
        # Ensure 'SocksPort' and 'ControlPort' in torrc_config are consistent or not set directly by user
        # as startTor will set them based on its direct parameters.
        # If they are in torrc_config, they might be overridden by startTor's logic.
        # For simplicity, we assume they are either not in torrc_config from ConfigManager,
        # or if they are, startTor's explicit params take precedence.

        return cls.startTor(
            port=int(port), # Ensure type
            control_port=int(control_port), # Ensure type
            host=str(host),
            password=password, # Can be None
            client_options=client_options,
            config=torrc_config, # This is the 'config' arg for startTor, used for torrc settings
            path=path, # Can be None
            own=own,
            max_circuit_dirtiness=max_circuit_dirtiness, # Can be None
            countries=countries # Can be None
        )

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

        if max_circuit_dirtiness is not None and max_circuit_dirtiness >= 10:
            config["MaxCircuitDirtiness"] = str(max_circuit_dirtiness)

        if countries is not None:
            config["ExitNodes"] = "{" + ",".join(countries) + "}"
            
        



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

    def stop(self) -> None:
        """
        Stop the Tor process if it was started by this instance.
        """
        if self.tor is None:
            print("Tor process was not started by this instance or is already stopped.")
            return

        try:
            print("Attempting to terminate Tor process...")
            self.tor.terminate()
            try:
                # Wait for a few seconds for the process to terminate
                self.tor.wait(timeout=5) # Python 3.3+
                print("Tor process terminated gracefully.")
            except AttributeError: # self.tor.wait() is not available in python 3.2
                 time.sleep(5) # wait 5 seconds
                 if self.tor.poll() is None: # check if process is still running
                    print("Tor process did not terminate gracefully, attempting to kill...")
                    self.tor.kill()
                    print("Tor process killed.")
                 else:
                    print("Tor process terminated gracefully.")
            except TimeoutError: # subprocess.TimeoutExpired in Python 3.3+
                print("Tor process did not terminate gracefully within timeout, attempting to kill...")
                self.tor.kill()
                # Wait a bit for kill to take effect
                time.sleep(2)
                if self.tor.poll() is None:
                    print("Failed to kill Tor process.")
                else:
                    print("Tor process killed.")
            except Exception as e: # Catch other potential exceptions during wait/poll
                print(f"An error occurred while waiting for Tor process to terminate: {e}")
                print("Attempting to kill Tor process...")
                self.tor.kill()
                time.sleep(2) # Wait a bit for kill to take effect
                if self.tor.poll() is None:
                    print("Failed to kill Tor process after error.")
                else:
                    print("Tor process killed after error.")

        except ProcessLookupError: # This can happen if the process is already dead
            print("Tor process was already stopped.")
        except Exception as e:
            print(f"An error occurred while trying to stop the Tor process: {e}")
        finally:
            self.tor = None