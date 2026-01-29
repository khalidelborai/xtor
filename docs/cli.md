<!-- markdownlint-disable -->

<a href="../xtor/cli.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `cli`
xtor CLI - Manage Tor instances. 


---

<a href="../xtor/cli.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_process_running`

```python
check_process_running(pid: 'int | None') → bool
```

Check if a process with given PID is running. 


---

<a href="../xtor/cli.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `start`

```python
start(
    name: 'str' = <typer.models.ArgumentInfo object at 0x7d81f2e66680>,
    port: 'int' = <typer.models.OptionInfo object at 0x7d81f2e66650>,
    control_port: 'int' = <typer.models.OptionInfo object at 0x7d81f2e659f0>,
    host: 'str' = <typer.models.OptionInfo object at 0x7d81f2e66dd0>,
    password: 'str | None' = <typer.models.OptionInfo object at 0x7d81f2e66d70>,
    countries: 'str | None' = <typer.models.OptionInfo object at 0x7d81f2e66ce0>,
    path: 'Path | None' = <typer.models.OptionInfo object at 0x7d81f2e66cb0>,
    max_time: 'int' = <typer.models.OptionInfo object at 0x7d81f2e66bc0>
) → None
```

Start a named Tor instance. 


---

<a href="../xtor/cli.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `stop`

```python
stop(name: 'str' = <typer.models.ArgumentInfo object at 0x7d81f2e67b20>) → None
```

Stop a named Tor instance. 


---

<a href="../xtor/cli.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `remove`

```python
remove(
    name: 'str' = <typer.models.ArgumentInfo object at 0x7d81f2e672b0>
) → None
```

Stop and remove a named Tor instance completely. 


---

<a href="../xtor/cli.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_cmd`

```python
list_cmd() → None
```

List all managed Tor instances. 


---

<a href="../xtor/cli.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `connect`

```python
connect(
    name: 'str' = <typer.models.ArgumentInfo object at 0x7d81f2e66aa0>
) → None
```

Show connection details for a named instance. 


---

<a href="../xtor/cli.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `main`

```python
main() → None
```

CLI entry point. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
