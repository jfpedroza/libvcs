(workflow)=

# Workflow

## Development environment

[poetry] is a required package to develop.

```console
$ git clone https://github.com/vcs-python/libvcs.git
```

```console
$ cd libvcs
```

```console
$ poetry install -E "docs test coverage lint format"
```

Makefile commands prefixed with `watch_` will watch files and rerun.

## Tests

```console
$ poetry run py.test
```

Helpers: `make test` Rerun tests on file change: `make watch_test` (requires [entr(1)])

## Documentation

Default preview server: http://localhost:8068

[sphinx-autobuild] will automatically build the docs, watch for file changes and launch a server.

From home directory: `make start_docs` From inside `docs/`: `make start`

[sphinx-autobuild]: https://github.com/executablebooks/sphinx-autobuild

### Manual documentation (the hard way)

`cd docs/` and `make html` to build. `make serve` to start http server.

Helpers: `make build_docs`, `make serve_docs`

Rebuild docs on file change: `make watch_docs` (requires [entr(1)])

Rebuild docs and run server via one terminal: `make dev_docs` (requires above, and a `make(1)` with
`-J` support, e.g. GNU Make)

## Formatting

The project uses [black] and [isort] (one after the other). Configurations are in `pyproject.toml`
and `setup.cfg`:

- `make black isort`: Run `black` first, then `isort` to handle import nuances

## Linting

[flake8] and [mypy] run via CI in our GitHub Actions. See the configuration in `pyproject.toml` and
`setup.cfg`.

### flake8

[flake8] provides fast, reliable, barebones styling and linting.

````{tab} Command

poetry:

```console
$ poetry run flake8
```

If you setup manually:

```console
$ flake8
```

````

````{tab} make

```console
$ make flake8
```

````

````{tab} Watch

```console
$ make watch_flake8
```

requires [`entr(1)`].

````

````{tab} Configuration

See `[flake8]` in setup.cfg.

```{literalinclude} ../../setup.cfg
:language: ini
:start-at: "[flake8]"
:end-before: "[isort]"

```

````

### mypy

[mypy] is used for static type checking.

````{tab} Command

poetry:

```console
$ poetry run mypy .
```

If you setup manually:

```console
$ mypy .
```

````

````{tab} make

```console
$ make mypy
```

````

````{tab} Watch

```console
$ make watch_mypy
```

requires [`entr(1)`].
````

## Releasing

Since this software used in production projects, we don't want to release breaking changes.

Choose what the next version is. Assuming it's version 0.9.0, it could be:

- 0.9.0post0: postrelease, if there was a packaging issue
- 0.9.1: bugfix / security / tweak
- 0.10.0: breaking changes, new features

Let's assume we pick 0.9.1

`CHANGES`: Assure any PRs merged since last release are mentioned. Give a thank you to the
contributor. Set the header with the new version and the date. Leave the "current" header and
_Insert changes/features/fixes for next release here_ at the top::

    current
    -------
    - *Insert changes/features/fixes for next release here*

    libvcs 0.9.1 (2020-10-12)
    -------------------------
    - :issue:`1`: Fix bug

`libvcs/__init__.py` and `__about__.py` - Set version

```console
$ git commit -m 'Tag v0.9.1'
```

```console
$ git tag v0.9.1
```

After `git push` and `git push --tags`, CI will automatically build and deploy to PyPI.

### Releasing (manual)

As of 0.10, [poetry] handles virtualenv creation, package requirements, versioning, building, and
publishing. Therefore there is no setup.py or requirements files.

Update `__version__` in `__about__.py` and `pyproject.toml`::

    git commit -m 'build(libvcs): Tag v0.1.1'
    git tag v0.1.1
    git push
    git push --tags
    poetry build
    poetry publish

[poetry]: https://python-poetry.org/
[entr(1)]: http://eradman.com/entrproject/
[`entr(1)`]: http://eradman.com/entrproject/
[black]: https://github.com/psf/black
[isort]: https://pypi.org/project/isort/
[flake8]: https://flake8.pycqa.org/
[mypy]: http://mypy-lang.org/
