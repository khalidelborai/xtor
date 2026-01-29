<!-- markdownlint-disable -->

<a href="../xtor/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
Utility functions for xtor. 


---

<a href="../xtor/utils.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_tor_pass_hash`

```python
get_tor_pass_hash(secret_password: str) → str
```

Generate a hashed password for Tor control port authentication. 



**Args:**
 
 - <b>`secret_password`</b>:  The plaintext password to hash. 



**Returns:**
 
 - <b>`A Tor-compatible hashed password string (format`</b>:  16:SALT+INDICATOR+HASH). 

Reference: 
 - <b>`https`</b>: //stackoverflow.com/a/67198518 


---

<a href="../xtor/utils.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_port_available`

```python
is_port_available(port: int, host: str = '127.0.0.1') → bool
```

Check if a port is available for binding. 



**Args:**
 
 - <b>`port`</b>:  The port number to check. 
 - <b>`host`</b>:  The host address to check (default: 127.0.0.1). 



**Returns:**
 True if the port is available, False if it's in use. 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If you want to raise instead of returning False,  use check_port_or_raise() instead. 


---

<a href="../xtor/utils.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_port_or_raise`

```python
check_port_or_raise(port: int, host: str = '127.0.0.1') → None
```

Check if a port is available, raising an exception if not. 



**Args:**
 
 - <b>`port`</b>:  The port number to check. 
 - <b>`host`</b>:  The host address to check (default: 127.0.0.1). 



**Raises:**
 
 - <b>`PortInUseError`</b>:  If the port is already in use. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
