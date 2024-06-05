# Avro Tools for Python

As documented in the [Apache Avro
docs](https://avro.apache.org/docs/1.11.1/getting-started-python/), this folder
contains python scripts for working with Avro files.

## Installation

This folder requires Python version 3.10 or later*. You'll need to install
dependencies before running the scripts here. We recommend installing these in
the local folder using a python virtual environment (venv), to avoid changing your
system's global python packages:

```
cd interface-gen
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
python interface-gen/generate.py
```

To run tests,

```
cd interface-gen
python -m unittest *test.py
```
