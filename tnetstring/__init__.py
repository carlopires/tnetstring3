"""Fast typed-netstring encoding and decoding."""

from __future__ import annotations

from typing import BinaryIO

from ._tnetstring import dumps, load, loads, pop

__all__ = ["dump", "dumps", "load", "loads", "pop"]
__version__ = "0.4.0"


def dump(value: object, file_handle: BinaryIO) -> None:
    """Encode one value and write it to a binary file-like object."""
    file_handle.write(dumps(value))
