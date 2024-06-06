# Avro Tools for Python

This folder contains python scripts for working with Avro IDL definitions, and generating code, schemas, and documentation from them.

These scripts utilize
[Apache Avro](https://avro.apache.org/docs/1.11.1/getting-started-python/)
and [avrotize](https://github.com/clemensv/avrotize).

## Installation

This folder requires Python version 3.10 or later*. You'll need to install
dependencies before running the scripts here. We recommend installing these in
the local folder using a python virtual environment (venv), to avoid changing your
system's global python packages:

```
python -m venv venv                             # create a local virtual env.
source venv/bin/activate                        # activate the virtual env.
python -m pip intstall -r requirements.txt      # install dependencies, e.g. avro, etc

```

To exit the virtualenv, simply run the command `deactivate` from your shell.

\* Note: The requirement for python >= 3.10 can be relaxed if it causes
trouble. We just need to change type annotation syntax a bit.

## Generating Schemas & Code, Running Tests

From the root of the repository, run:

```
python -m interface_gen/generate --help
```

to see usage information. For example, let's say you have this directory
structure where you store your protocol definitions:

```
├── my-protocols
│   ├── v1.1
│   |   └── foo.avdl
│   └── v2.0
│       └── foo.avdl
│
├── docs
```

Running this command:

```
python -m interface_gen/generate -i -p my-protocols -d docs
```
Will do the following:

- Install any toolchain dependencies, if needed (`-i`)
- Generate schemas for both versions of `foo.avdl` (avro and protobuf)
- Generate documentation for the same, placed in `docs/`


## Running Tests

To run tests,

```
cd interface_gen
python -m unittest *test.py
```
