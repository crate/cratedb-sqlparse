# Developer Guide for cratedb-sqlparse

About building locally, or using a different CrateDB version.

> The generated parser is not uploaded to the repository because it is huge.
> To use the package locally or to build a different version use the build script.

## Setup

To start things off, bootstrap the sandbox environment.

### Acquire sources
```shell
git clone git@github.com:crate/cratedb-sqlparse.git
cd cratedb-sqlparse
```

### Install dependencies
```
pip install -r requirements.txt
```

### Generate grammar files
```shell
poe generate
```


## Running Tests for Python

First, navigate to the corresponding subdirectory:

    cd cratedb_sqlparse_py

Verify code by running all linters and software tests:

    poe check

Run specific tests:

    pytest -k enricher
    pytest -k lexer

Format code:

    poe format


## Running Tests for JavaScript

First, navigate to the corresponding subdirectory:

    cd cratedb_sqlparse_js

Set up project:

    npm install

Verify code by running all linters and software tests:

    npm test

Run specific tests:

    ???

Format code:

    ???



## Running a Release

### Python

Overview:
- Versioning happens automatically based on the `versioningit` package.
  You just need to tag the repository.
- Package building and publishing happens automatically, being staged
  through GHA to PyPI.

On branch `main`:
- Add a section for the new version in the `CHANGES.md` file.
- Commit your changes with a message like `Release vx.y.z`.
- Create a tag, and push to remote.
  This will trigger a GitHub action which releases the new version to PyPI.
  ```shell
  git tag v0.0.3
  git push --tags
  ```
- On GitHub, designate a new release, copying in the relevant section
  from the CHANGELOG.
  https://github.com/crate/cratedb-sqlparse/releases

Optionally, build the package and upload to PyPI manually.
```shell
poe release
```


### JavaScript

Overview:
- Versioning happens manually on behalf of the `package.json` file.
- Package building and publishing to npmjs.com happens manually, using
  the `npm` program.

On branch `main`:
- Make sure to run `poe generate` on the root folder first.
- Adjust version number in `package.json`.
- Generate `package-lock.json`.

      npm install --package-lock-only

- Commit your changes with a message like `Release vx.y.z`.
- Create a tag, and push to remote.
- Build package.

      npm run build

- Publish package.

      npm login
      npm publish
