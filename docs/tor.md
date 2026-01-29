<!-- markdownlint-disable -->

<a href="../xtor/tor.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `tor`




**Global Variables**
---------------
- **DEFAULT_IP_CHECK_URL**

---

<a href="../xtor/tor.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_password`

```python
generate_password(length: 'int' = 16) → str
```

Generate a secure random password. 


---

<a href="../xtor/tor.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HiddenService`
Information about an ephemeral hidden service. 

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    hostname: 'str',
    ports: 'dict[int, tuple[str, int]]',
    private_key: 'str | None' = None
) → None
```






---

#### <kbd>property</kbd> onion_address

Get the full .onion address. 




---

<a href="../xtor/tor.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExitNodeInfo`
Information about the current Tor exit node. 

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    fingerprint: 'str',
    nickname: 'str',
    address: 'str',
    country: 'str | None',
    bandwidth: 'int | None',
    flags: 'list[str]'
) → None
```









---

<a href="../xtor/tor.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Tor`
Tor instance for managing Tor connections and HTTP clients. 

Can be used in two ways: 1. Connect to an existing Tor instance via constructor 2. Launch a new Tor process via Tor.start() class method 



**Example:**
  # Connect to existing Tor  with Tor(password="mypass", port=9050, control_port=9051) as tor:  print(tor.ip) 

 # Launch new Tor process  with Tor.start(port=9050, control_port=9051, host="127.0.0.1", password="mypass") as tor:  response = tor.client.get("https://example.com") 

<a href="../xtor/tor.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    password: 'str',
    port: 'int' = 9050,
    control_port: 'int' = 9051,
    host: 'str | None' = '127.0.0.1',
    client_options: 'dict[str, Any] | None' = None,
    tor: 'Popen | None' = None,
    ip_check_url: 'str' = 'https://api.ipify.org',
    client_timeout: 'float' = 30.0,
    name: 'str | None' = None
) → None
```

Initialize a Tor instance to connect to an existing Tor process. 



**Args:**
 
 - <b>`password`</b>:  Password for Tor control port authentication. 
 - <b>`port`</b>:  SOCKS port for Tor proxy. Defaults to 9050. 
 - <b>`control_port`</b>:  Control port for Tor commands. Defaults to 9051. 
 - <b>`host`</b>:  Host address for Tor. Defaults to "127.0.0.1". 
 - <b>`client_options`</b>:  Additional options to pass to httpx.Client. Defaults to None. 
 - <b>`tor`</b>:  Existing Tor subprocess (used internally by start()). Defaults to None. 
 - <b>`ip_check_url`</b>:  URL to use for IP address lookups. Defaults to "https://api.ipify.org". 
 - <b>`client_timeout`</b>:  Timeout in seconds for HTTP client requests. Defaults to 30.0. 
 - <b>`name`</b>:  Name for this instance (used for state persistence). Defaults to None. 



**Raises:**
 
 - <b>`ConnectionError`</b>:  If connection to the Tor control port fails. 


---

#### <kbd>property</kbd> can_new_identity

Check if new identity request is available (rate limited to 10s). 

---

#### <kbd>property</kbd> exit_node

Get current exit node information. 

---

#### <kbd>property</kbd> is_alive

Check if Tor controller connection is alive. 

---

#### <kbd>property</kbd> newnym_wait

Get seconds until new identity request is available. 

---

#### <kbd>property</kbd> uptime

Get Tor process uptime. 

---

#### <kbd>property</kbd> version

Get Tor version string. 



---

<a href="../xtor/tor.py#L538"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_event_listener`

```python
add_event_listener(event_type: 'str', callback: 'Callable') → None
```

Subscribe to Tor controller events. 



**Args:**
 
 - <b>`event_type`</b>:  Event type to listen for. Common types: 
        - "CIRC": Circuit events (built, closed, failed) 
        - "STREAM": Stream events (new connections) 
        - "BW": Bandwidth events (bytes read/written) 
        - "NEWDESC": New relay descriptors 
        - "ADDRMAP": Address mapping events 
        - "SIGNAL": Signal events 
 - <b>`callback`</b>:  Function to call when event occurs. Receives event object. 



**Example:**
 def on_circuit(event):  print(f"Circuit {event.id}: {event.status}") 

tor.add_event_listener("CIRC", on_circuit) 

---

<a href="../xtor/tor.py#L614"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `attach_stream`

```python
attach_stream(stream_id: 'str | int', circuit_id: 'str | int') → None
```

Attach a stream to a specific circuit. 



**Args:**
 
 - <b>`stream_id`</b>:  The stream ID to attach. 
 - <b>`circuit_id`</b>:  The circuit ID to attach to. 

---

<a href="../xtor/tor.py#L596"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close_circuit`

```python
close_circuit(circuit_id: 'str | int') → None
```

Close a specific Tor circuit. 



**Args:**
 
 - <b>`circuit_id`</b>:  The circuit ID to close. 

---

<a href="../xtor/tor.py#L352"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `connect`

```python
connect() → None
```

Authenticate with the Tor controller. 



**Raises:**
 
 - <b>`AuthenticationError`</b>:  If authentication fails. 

---

<a href="../xtor/tor.py#L673"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_hidden_service`

```python
create_hidden_service(
    ports: 'dict[int, int | tuple[str, int]]',
    key_type: 'str' = 'NEW',
    key_content: 'str' = 'ED25519-V3',
    discard_key: 'bool' = False,
    detached: 'bool' = False,
    await_publication: 'bool' = False
) → HiddenService
```

Create an ephemeral hidden service (.onion address). 



**Args:**
 
 - <b>`ports`</b>:  Port mapping. Keys are virtual ports (what clients connect to),  values are target ports or (host, port) tuples. 
 - <b>`Example`</b>:  {80: 8080} or {80: ("127.0.0.1", 8080)} 
 - <b>`key_type`</b>:  Key type, "NEW" for new key or "ED25519-V3"/"RSA1024" for existing. 
 - <b>`key_content`</b>:  Key content or "ED25519-V3"/"RSA1024" for new key generation. 
 - <b>`discard_key`</b>:  If True, don't return private key (more secure, but can't recreate). 
 - <b>`detached`</b>:  If True, service persists after controller disconnects. 
 - <b>`await_publication`</b>:  If True, wait for service to be published to HSDir. 



**Returns:**
 
 - <b>`HiddenService`</b>:  The created hidden service with hostname and ports. 



**Example:**
 # Create service mapping .onion:80 -> localhost:8080 service = tor.create_hidden_service({80: 8080}) print(f"Service at: {service.onion_address}") 

---

<a href="../xtor/tor.py#L366"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `disconnect`

```python
disconnect() → None
```

Close the Tor controller connection. 

---

<a href="../xtor/tor.py#L261"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_name`

```python
from_name(name: 'str') → Tor
```

Connect to an existing named Tor instance. 



**Args:**
 
 - <b>`name`</b>:  Name of the instance to connect to. 



**Returns:**
 
 - <b>`Tor`</b>:  Connected Tor instance. 



**Raises:**
 
 - <b>`ValueError`</b>:  If instance not found. 

---

<a href="../xtor/tor.py#L583"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_circuits`

```python
get_circuits() → list
```

Get all current Tor circuits. 



**Returns:**
 
 - <b>`list`</b>:  List of Circuit objects from stem with attributes: 
        - id: Circuit ID 
        - status: Circuit status (BUILT, EXTENDED, etc.) 
        - path: List of (fingerprint, nickname) tuples for relays 
        - purpose: Circuit purpose (GENERAL, HS_CLIENT, etc.) 

---

<a href="../xtor/tor.py#L624"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_exit_node_info`

```python
get_exit_node_info() → ExitNodeInfo | None
```

Get detailed information about the current exit node. 



**Returns:**
 
 - <b>`ExitNodeInfo`</b>:  Exit node details including country, bandwidth, flags. 
 - <b>`None`</b>:  If no circuit is available or exit node info cannot be determined. 

---

<a href="../xtor/tor.py#L605"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_streams`

```python
get_streams() → list
```

Get all current Tor streams. 



**Returns:**
 
 - <b>`list`</b>:  List of stream info with target addresses and circuit IDs. 

---

<a href="../xtor/tor.py#L336"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `isolated_async_client`

```python
isolated_async_client(isolation_key: 'str') → AsyncClient
```

Get an async HTTP client with stream isolation. 



**Args:**
 
 - <b>`isolation_key`</b>:  Unique key for circuit isolation. 



**Returns:**
 
 - <b>`AsyncClient`</b>:  httpx AsyncClient with isolated circuit. 

---

<a href="../xtor/tor.py#L317"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `isolated_client`

```python
isolated_client(isolation_key: 'str') → Client
```

Get an HTTP client with stream isolation. 

Different isolation keys use different Tor circuits, preventing traffic correlation between requests. 



**Args:**
 
 - <b>`isolation_key`</b>:  Unique key for circuit isolation. Same key = same circuit. 



**Returns:**
 
 - <b>`Client`</b>:  httpx Client with isolated circuit. 

---

<a href="../xtor/tor.py#L473"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `kill`

```python
kill() → None
```

Kill the Tor process (if started via start()). 

Does nothing if no Tor process is associated with this instance. 

---

<a href="../xtor/tor.py#L748"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_hidden_services`

```python
list_hidden_services() → list[str]
```

List hostnames of active ephemeral hidden services. 



**Returns:**
 
 - <b>`list[str]`</b>:  List of .onion hostnames. 

---

<a href="../xtor/tor.py#L429"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `new_identity`

```python
new_identity(
    wait: 'bool' = False,
    timeout: 'float' = 30.0,
    poll_interval: 'float' = 0.5
) → None
```

Request a new Tor identity (new circuit/IP). 



**Args:**
 
 - <b>`wait`</b>:  If True, wait until IP actually changes. Defaults to False. 
 - <b>`timeout`</b>:  Maximum time in seconds to wait for IP change. Defaults to 30.0. 
 - <b>`poll_interval`</b>:  Time in seconds between IP checks. Defaults to 0.5. 



**Raises:**
 
 - <b>`IdentityChangeTimeout`</b>:  If wait=True and IP doesn't change within timeout. 

---

<a href="../xtor/tor.py#L570"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_event_listener`

```python
remove_event_listener(callback: 'Callable') → None
```

Remove an event listener callback. 



**Args:**
 
 - <b>`callback`</b>:  The callback function to remove. 

---

<a href="../xtor/tor.py#L735"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_hidden_service`

```python
remove_hidden_service(service: 'HiddenService | str') → None
```

Remove an ephemeral hidden service. 



**Args:**
 
 - <b>`service`</b>:  HiddenService object or .onion hostname string. 

---

<a href="../xtor/tor.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    port: 'int',
    control_port: 'int',
    host: 'str',
    password: 'str | None' = None,
    client_options: 'dict[str, Any] | None' = None,
    config: 'dict[str, Any] | None' = None,
    path: 'str | None' = None,
    own: 'bool | None' = True,
    max_circuit_dirtiness: 'int | None' = None,
    countries: 'list[str] | None' = None,
    ip_check_url: 'str' = 'https://api.ipify.org',
    client_timeout: 'float' = 30.0,
    name: 'str | None' = None,
    *args,
    **kwargs
) → Tor
```

Start a new Tor process and return a connected Tor instance. 



**Args:**
 
 - <b>`port`</b>:  SOCKS port for Tor proxy. 
 - <b>`control_port`</b>:  Control port for Tor commands. 
 - <b>`host`</b>:  Host address for Tor. 
 - <b>`password`</b>:  Password for Tor control port authentication. Defaults to None. 
 - <b>`client_options`</b>:  Additional options to pass to httpx.Client. Defaults to None. 
 - <b>`config`</b>:  Additional Tor configuration options. Defaults to None. 
 - <b>`path`</b>:  Path to tor binary. If None, searches system PATH. 
 - <b>`own`</b>:  Assert ownership over Tor process (aborts if Python terminates). Defaults to True. 
 - <b>`max_circuit_dirtiness`</b>:  Maximum time in seconds a circuit can be reused. Minimum 10. 
 - <b>`countries`</b>:  List of country codes for exit nodes (e.g., ["US", "DE"]). 
 - <b>`ip_check_url`</b>:  URL to use for IP address lookups. Defaults to "https://api.ipify.org". 
 - <b>`client_timeout`</b>:  Timeout in seconds for HTTP client requests. Defaults to 30.0. 
 - <b>`name`</b>:  Name for this instance (for state persistence). Defaults to None. 
 - <b>`*args`</b>:  Additional positional arguments for launch_tor_with_config. 
 - <b>`**kwargs`</b>:  Additional keyword arguments for launch_tor_with_config. 



**Raises:**
 
 - <b>`TorNotFoundError`</b>:  If tor binary cannot be found. 
 - <b>`PortInUseError`</b>:  If the requested port is already in use. 



**Returns:**
 
 - <b>`Tor`</b>:  Connected Tor instance. 

---

<a href="../xtor/tor.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start(
    port: 'int',
    control_port: 'int',
    host: 'str',
    password: 'str | None' = None,
    client_options: 'dict[str, Any] | None' = None,
    config: 'dict[str, Any] | None' = None,
    path: 'str | None' = None,
    own: 'bool | None' = True,
    max_circuit_dirtiness: 'int | None' = None,
    countries: 'list[str] | None' = None,
    ip_check_url: 'str' = 'https://api.ipify.org',
    client_timeout: 'float' = 30.0,
    name: 'str | None' = None,
    *args,
    **kwargs
) → Tor
```

Start a new Tor process and return a connected Tor instance. 



**Args:**
 
 - <b>`port`</b>:  SOCKS port for Tor proxy. 
 - <b>`control_port`</b>:  Control port for Tor commands. 
 - <b>`host`</b>:  Host address for Tor. 
 - <b>`password`</b>:  Password for Tor control port authentication. Defaults to None. 
 - <b>`client_options`</b>:  Additional options to pass to httpx.Client. Defaults to None. 
 - <b>`config`</b>:  Additional Tor configuration options. Defaults to None. 
 - <b>`path`</b>:  Path to tor binary. If None, searches system PATH. 
 - <b>`own`</b>:  Assert ownership over Tor process (aborts if Python terminates). Defaults to True. 
 - <b>`max_circuit_dirtiness`</b>:  Maximum time in seconds a circuit can be reused. Minimum 10. 
 - <b>`countries`</b>:  List of country codes for exit nodes (e.g., ["US", "DE"]). 
 - <b>`ip_check_url`</b>:  URL to use for IP address lookups. Defaults to "https://api.ipify.org". 
 - <b>`client_timeout`</b>:  Timeout in seconds for HTTP client requests. Defaults to 30.0. 
 - <b>`name`</b>:  Name for this instance (for state persistence). Defaults to None. 
 - <b>`*args`</b>:  Additional positional arguments for launch_tor_with_config. 
 - <b>`**kwargs`</b>:  Additional keyword arguments for launch_tor_with_config. 



**Raises:**
 
 - <b>`TorNotFoundError`</b>:  If tor binary cannot be found. 
 - <b>`PortInUseError`</b>:  If the requested port is already in use. 



**Returns:**
 
 - <b>`Tor`</b>:  Connected Tor instance. 

---

<a href="../xtor/tor.py#L491"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stop`

```python
stop() → None
```

Stop a named instance and remove from state. 

For unnamed instances, same as terminate(). 

---

<a href="../xtor/tor.py#L482"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `terminate`

```python
terminate() → None
```

Terminate the Tor process gracefully (if started via start()). 

Does nothing if no Tor process is associated with this instance. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
