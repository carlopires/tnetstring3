# tnetstring3

`tnetstring3` is a compact C implementation of
[typed netstrings](https://tnetstrings.info/) for Python. Typed netstrings prefix each payload
with its byte length and use a one-byte type tag, providing an unambiguous binary format without
text encoding rules.

The package supports CPython 3.10 and newer. Its native extension declares and tests support for
free-threaded CPython, including CPython 3.14t.

## Installation

```console
python -m pip install tnetstring3
```

Installing from a source distribution requires a C compiler and Python development headers.

## Usage

```python
import tnetstring

value = {
    b"name": b"example",
    b"size": 42,
    b"active": True,
    b"parts": [b"a", b"b"],
}

encoded = tnetstring.dumps(value)
assert tnetstring.loads(encoded) == value
```

The public API is:

- `dumps(value) -> bytes`: encode one value.
- `loads(data: bytes) -> object`: decode one value.
- `pop(data: bytes) -> tuple[object, bytes]`: decode the first value and return the remainder.
- `dump(value, file_handle) -> None`: encode and write one value.
- `load(file_handle) -> object`: read and decode exactly one value.

Supported values are `bytes`, `int`, `float`, `bool`, `None`, `list`, and dictionaries whose keys
and values are supported values. Strings are binary blobs in the typed-netstring protocol, so
Python `str` values are intentionally rejected; applications must choose an encoding explicitly.

## Free-threaded CPython

The C extension does not enable the GIL when imported by a free-threaded CPython build. Encoding
copies each mutable list or dictionary before traversing it, preventing unsafe borrowed references
when another thread mutates the same container.

Those per-container copies do not make a nested object graph transactionally atomic. If an
application requires one coherent point-in-time view across several mutable containers, it must
synchronize the mutation and encoding itself.

## Development

Run the tests against an installed build so they exercise the native extension:

```console
python -m pip install -e .
python -m unittest discover -v -s tests
```

Release and artifact validation steps are documented in [RELEASING.md](RELEASING.md).

## License

MIT. See [LICENSE.txt](LICENSE.txt).
