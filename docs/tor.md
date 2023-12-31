<!-- markdownlint-disable -->

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `tor`






---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Tor`




<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    password: str,
    port: int = 9050,
    control_port: int = 9051,
    host: Optional[str] = '127.0.0.1',
    client_options: Optional[dict] = {},
    tor: Optional[Popen] = None
) → None
```

Tor instance 



**Args:**
 
 - <b>`password`</b> (str):  Password to use for Tor 
 - <b>`port`</b> (int, optional):  Port to use for Tor. Defaults to 9050. 
 - <b>`control_port`</b> (int, optional):  Control port to use for Tor. Defaults to 9051. 
 - <b>`host`</b> (Optional[str], optional):  Host to use for Tor. Defaults to " 
 - <b>`client_options`</b> (Optional[dict], optional):  Client options to use for Tor. Defaults to {}. 
 - <b>`tor`</b> (Optional[Popen], optional):  Tor process. Defaults to None. 


---

#### <kbd>property</kbd> client

Get httpx Client 



**Returns:**
 
 - <b>`Client`</b>:  httpx Client 

---

#### <kbd>property</kbd> ip

Get connected instance IP 



**Returns:**
 
 - <b>`str`</b>:  instance IP 



---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `connect`

```python
connect() → None
```

Connect to Tor 

---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `disconnect`

```python
disconnect() → None
```

Disconnect from Tor 

---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L190"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `kill`

```python
kill() → None
```

Kill Tor process 

---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `new_identity`

```python
new_identity(wait=False) → None
```

Get new identity 

---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `startTor`

```python
startTor(
    port: int,
    control_port: int,
    host: str,
    password: Optional[str] = None,
    client_options: Optional[dict] = {},
    config: Optional[dict] = {},
    path: Optional[str] = None,
    own: Optional[bool] = True,
    *args,
    **kwargs
) → Tor
```

Start Tor 



**Args:**
 
 - <b>`port`</b> (int):  Port to use for Tor 
 - <b>`control_port`</b> (int):  Control port to use for Tor 
 - <b>`host`</b> (str):  Host to use for Tor 
 - <b>`password`</b> (Optional[str], optional):  Password to use for Tor. Defaults to None. 
 - <b>`client_options`</b> (Optional[dict], optional):  Client options to use for Tor. Defaults to {}. 
 - <b>`config`</b> (Optional[dict], optional):  Tor instance additional config 
 - <b>`own`</b> (Optional[bool], optional):  asserts ownership over the tor process so it aborts if this python process terminates or a `Controller` we establish to it disconnects 



**Raises:**
 
 - <b>`Exception`</b>:  If port is already in use 
 - <b>`Exception`</b>:  If control_port is already in use 



**Returns:**
 
 - <b>`Tor`</b>:  Tor instance 

---

<a href="https://github.com/khalidelborai/xtor/blob/master/xtor/tor.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `terminate`

```python
terminate() → None
```

Terminate Tor process 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
