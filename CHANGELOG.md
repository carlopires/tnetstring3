# Changelog

## 0.4.0 - 2026-08-01

- Add native support for free-threaded CPython without enabling the GIL.
- Snapshot mutable list and dictionary values during concurrent encoding.
- Stop mutating immutable input while parsing large integers.
- Add bounds, overflow, recursion, and malformed-input validation to the C parser.
- Fix reference and output-buffer leaks in file loading and value rendering.
- Move the extension into the `tnetstring` package and remove the unused Python fallback.
- Adopt PEP 517/621 packaging and require Python 3.10 or newer.

## 0.3.1 - 2014-07-20

- Correct release metadata after the Python 3 port.

## 0.3.0 - 2014-07-20

- Support Python 3 only. Use version 0.2.1 for Python 2.
- Remove encoding arguments; typed-netstring strings are exposed as bytes.

## 0.2.1

- Fix a memory leak in `tnetstring.pop()`.
- Fix handling of large integers.

## 0.2.0

- Add optional application-level Unicode encoding support.

## 0.1.0

- Initial release.
