# Developer Guide for cratedb-sqlparse

Libraries in this repository are not usable without building the necessary files with `setup_grammar.py`,
this is because the generated parser is not uploaded to the repository. Every target language, e.g:
Python or JavaScript, needs to be built independently.

The build script should not have any side effect, meaning you should be able to re-build with
a different CrateDB version without any extra work.

## Running the build script.

### Acquire sources
```shell
git clone git@github.com:crate/cratedb-sqlparse.git
cd cratedb-sqlparse
```

### Setup uv
[uv](https://docs.astral.sh/uv/) is used across the project and is the recommended dependency tool, both for building the
project's grammar and the development of the Python target.

macOS and Linux:
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:
```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If those options don't work, see https://docs.astral.sh/uv/getting-started/installation/

### Install dependencies
```shell
pip install -r requirements.txt
```

or uv

```shell
uv pip install -r requirements.txt
```

### Generate grammar files

Python:
```shell
uv run python setup_grammar.py python
```

Javascript:
```shell
uv run python setup_grammar.py javascript
```

Now libraries that were built are ready to use, every library e.g. `cratedb_sqlparse_js`
are on themselves different projects, with their own dependencies and
dependency management systems.

## Setting up cratedb_sqlparse_py

In `./cratedb_sqlparse_py` run


### Set up dependencies

```shell
uv sync --all-groups
```

### Run tests

```shell
uv run pytest
```

### Format code:
```shell
uv run poe format
```

## Running Tests for JavaScript
In `./cratedb_sqlparse_js` run:

## Setup dependencies
```shell
npm install
```

## Run tests
```shell
npm test
```

## Releasing libraries.
Releases are done on GitHub, by creating a [new release](https://github.com/crate/cratedb-sqlparse/releases)
every library will be built and published.

1. Make sure that in `setup_grammar.py` the CrateDB version matches the one you want.
2. On GitHub create a new release, creating the appropriate tag and adapting the changelog.

### Python
Releases to https://pypi.org/project/cratedb-sqlparse/

Overview:
- Versioning happens automatically based on the `versioningit` package.

#### Manual release.
Optionally, build the package and upload to PyPI manually.
```shell
uv run poe release
```

### JavaScript
Releases to https://www.npmjs.com/package/@cratedb/cratedb-sqlparse

Overview:
- Versioning is manual.

#### Manual release
Make sure to run `poe generate` on the root folder first and adjust version number in `package.json`.

Then run:
```shell
npm install &&
npm run build &&
npm login &&
npm publish
```
