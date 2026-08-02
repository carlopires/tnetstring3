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
CPython wheels cannot be installed by free-threaded interpreters.

Push the release commit to `master`, wait for CI, and manually run the `Release` workflow against
`master`. Review its Linux, macOS, Windows, and source-distribution artifacts before tagging. A
manual workflow run never publishes.

## Publish

PyPI Trusted Publishing must identify this repository, `.github/workflows/release-artifacts.yml`,
and the `pypi` environment. The matching GitHub environment must require approval before a
deployment can proceed.

Create and push the signed release tag only after the manual artifact run succeeds:

```console
git tag -s v0.4.0 -m "tnetstring3 0.4.0"
git push origin master v0.4.0
```

The tag runs the same artifact build. Once every artifact job succeeds, review and approve the
`pypi` deployment. The isolated publish job downloads those artifacts and uploads them with a
short-lived OIDC credential; it has no checkout or build step and uses no persistent PyPI token.

PyPI releases are immutable. Do not reuse a version after any artifact has been uploaded.
