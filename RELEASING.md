# Releasing tnetstring3

## Preconditions

1. Update `tnetstring.__version__` and `CHANGELOG.md` in the release commit.
2. Confirm the version does not already exist on PyPI.
3. Run tests on regular and free-threaded CPython.
4. Build from a clean Git worktree.

## Local validation

Build and validate the source distribution:

```console
uv build --sdist --clear
uvx twine check dist/*.tar.gz
```

Install the source distribution in a clean environment and run its included tests:

```console
uv venv --python 3.10 /tmp/tnetstring3-release-test
uv pip install --python /tmp/tnetstring3-release-test/bin/python dist/tnetstring3-0.4.0.tar.gz
cd /tmp
/tmp/tnetstring3-release-test/bin/python -m unittest discover -v \
  -s /path/to/tnetstring3/tests
```

Use `cibuildwheel` with the configuration in `pyproject.toml` to build portable wheels into a
separate `wheelhouse` directory. In particular, retain and test the `cp314t` artifacts; regular
CPython wheels cannot be installed by free-threaded interpreters. Pushing the release tag runs the
artifact-only GitHub workflow for Linux, macOS, and Windows. It intentionally does not publish to
PyPI.

## Publish

Create and push the signed release tag only after artifact review:

```console
git tag -s v0.4.0 -m "tnetstring3 0.4.0"
git push origin master v0.4.0
```

Download the CI artifacts into one clean release directory. Upload only the reviewed source
distribution and portable `cibuildwheel` wheels using a scoped PyPI token or Trusted Publishing:

```console
uv publish release/*
```

PyPI releases are immutable. Do not reuse a version after any artifact has been uploaded.
