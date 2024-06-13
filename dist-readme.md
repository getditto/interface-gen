# Interface Generator

Write your protocol specifications in a single language (Avro IDL) and
automatically generate schema definitions, code, and documentation for multiple
languages and serialization frameworks, including:

- Protobuf (proto3)
- Apache Avro Schema (.avsc)
- JSON schema
- XML schema
- SQL DDL (create table)
- .. and of the other formats supported by [Avrotize](https://github.com/clemensv/avrotize).

## Quick Start

1. Create a virtual environment (optional but recommended), and activate it:

```
python -m venv venv
source venv/bin/activate

```

2. Install the package:

```
python -m pip install interface-gen
```

3. Set up your protocol definitions and output directory.

```
mkdir -p my-protocols/v1.0
mkdir my-output
```

Place your Avro IDL definition files (.avdl)  in `my-protocols/v1.0`

4. Run the generator:

```
ifgen -i -p my-protocols -o my-output
```

## More Details

For more details see the source code docs:

- Python [interface\_gen/README.md](https://github.com/getditto/interface_gen/blob/main/README.md)
- Main [README.md](https://github.com/getditto/interface-gen/blob/main/README.md)
- The [code repostitory](https://github.com/getditto/interface-gen)

