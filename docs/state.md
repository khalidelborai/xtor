<!-- markdownlint-disable -->

<a href="../xtor/state.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `state`
State management for named Tor instances. 


---

<a href="../xtor/state.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_xtor_dir`

```python
get_xtor_dir() → Path
```

Get the xtor config directory, creating if needed. 


---

<a href="../xtor/state.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_instances_dir`

```python
get_instances_dir() → Path
```

Get the instances data directory, creating if needed. 


---

<a href="../xtor/state.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `read_state`

```python
read_state() → dict[str, dict]
```

Read all instance state from disk. 


---

<a href="../xtor/state.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `write_state`

```python
write_state(state: 'dict[str, dict]') → None
```

Write instance state to disk with secure permissions. 


---

<a href="../xtor/state.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_instance`

```python
get_instance(name: 'str') → InstanceState | None
```

Get a specific instance's state. 


---

<a href="../xtor/state.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `save_instance`

```python
save_instance(instance: 'InstanceState') → None
```

Save an instance's state. 


---

<a href="../xtor/state.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `remove_instance`

```python
remove_instance(name: 'str') → bool
```

Remove an instance from state. Returns True if found and removed. 


---

<a href="../xtor/state.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_instances`

```python
list_instances() → list[InstanceState]
```

List all saved instances. 


---

<a href="../xtor/state.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_instance_data_dir`

```python
get_instance_data_dir(name: 'str') → Path
```

Get or create the data directory for a named instance. 


---

<a href="../xtor/state.py#L133"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `remove_instance_data_dir`

```python
remove_instance_data_dir(name: 'str') → bool
```

Remove the data directory for a named instance. 


---

<a href="../xtor/state.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `InstanceState`
State for a named Tor instance. 

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    name: 'str',
    pid: 'int | None',
    port: 'int',
    control_port: 'int',
    password: 'str',
    host: 'str' = '127.0.0.1',
    data_dir: 'str | None' = None
) → None
```








---

<a href="../xtor/state.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_dict`

```python
from_dict(name: 'str', data: 'dict') → InstanceState
```





---

<a href="../xtor/state.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict() → dict
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
