<!-- markdownlint-disable -->

<a href="../xtor/pool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `pool`
TorPool - Manage multiple Tor instances for high-throughput applications. 



---

<a href="../xtor/pool.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TorPool`
Pool of Tor instances for parallel requests with automatic port allocation. 

Manages multiple Tor processes with round-robin or random selection, automatic port allocation, and bulk identity rotation. 



**Example:**
  with TorPool(size=3, base_port=9100, password="secret") as pool:  # Round-robin selection  for url in urls:  tor = pool.next()  response = tor.client.get(url) 

 # Rotate all identities  pool.rotate_all() 

 # Random selection  tor = pool.random() 

<a href="../xtor/pool.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    size: 'int',
    base_port: 'int' = 9100,
    password: 'str | None' = None,
    host: 'str' = '127.0.0.1',
    countries: 'list[str] | None' = None,
    client_timeout: 'float' = 30.0
) → None
```

Initialize a Tor pool. 



**Args:**
 
 - <b>`size`</b>:  Number of Tor instances to manage. 
 - <b>`base_port`</b>:  Starting port for SOCKS proxies. Control ports start at base_port + 100. 
 - <b>`password`</b>:  Password for Tor control ports. 
 - <b>`host`</b>:  Host address for Tor instances. 
 - <b>`countries`</b>:  List of country codes for exit nodes. 
 - <b>`client_timeout`</b>:  HTTP client timeout in seconds. 


---

#### <kbd>property</kbd> instances

Get all Tor instances in the pool. 

---

#### <kbd>property</kbd> ips

Get IP addresses of all instances. 



---

<a href="../xtor/pool.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get`

```python
get(index: 'int') → Tor
```

Get a specific Tor instance by index. 



**Args:**
 
 - <b>`index`</b>:  Instance index (0 to size-1). 



**Returns:**
 
 - <b>`Tor`</b>:  Tor instance at the given index. 

---

<a href="../xtor/pool.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `next`

```python
next() → Tor
```

Get next Tor instance using round-robin selection. 



**Returns:**
 
 - <b>`Tor`</b>:  Next Tor instance in rotation. 

---

<a href="../xtor/pool.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `random`

```python
random() → Tor
```

Get a random Tor instance from the pool. 



**Returns:**
 
 - <b>`Tor`</b>:  Random Tor instance. 

---

<a href="../xtor/pool.py#L141"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rotate_all`

```python
rotate_all(wait: 'bool' = False, timeout: 'float' = 30.0) → None
```

Request new identity on all Tor instances. 



**Args:**
 
 - <b>`wait`</b>:  If True, wait for IP to change on each instance. 
 - <b>`timeout`</b>:  Maximum seconds to wait per instance. 

---

<a href="../xtor/pool.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rotate_one`

```python
rotate_one(wait: 'bool' = False, timeout: 'float' = 30.0) → Tor
```

Rotate identity on one instance (the next in round-robin). 



**Args:**
 
 - <b>`wait`</b>:  If True, wait for IP to change. 
 - <b>`timeout`</b>:  Maximum seconds to wait. 



**Returns:**
 
 - <b>`Tor`</b>:  The rotated instance. 

---

<a href="../xtor/pool.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start() → TorPool
```

Start all Tor instances in the pool. 



**Returns:**
 
 - <b>`TorPool`</b>:  Self for method chaining. 

---

<a href="../xtor/pool.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stop`

```python
stop() → None
```

Stop all Tor instances in the pool. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
