from __future__ import annotations
import avro.datafile
import avro.schema
import avro.io
from fastavro.validation import validate as fastavro_validate
import json
import os
import unittest


def schema_filename(name: str, version: str) -> str:
    script_dir = os.path.dirname(__file__)
    path = os.path.join(script_dir, "..", "protocol", f"v{version}",
                        "schema", f"{name}.avsc")
    return os.path.abspath(path)


class Protocol:

    def __init__(self, schema_name: str, version: str):
        self.schema_name = schema_name
        self.version = version
        self.schema_fn: str = schema_filename(schema_name, version)
        if not os.path.exists(self.schema_fn):
            raise ValueError(f"Schema file {self.schema_fn} does not exist")

    def example_data_filename(self, extension="json") -> str:
        script_dir = os.path.dirname(__file__)
        path = os.path.join(script_dir, "..", "example_data")
        path = os.path.join(path, f"v{self.version}", f"{self.schema_name}.{extension}")
        return os.path.abspath(path)

    def validate_schema(self):
        print(f"--> Reading schema {self.schema_fn} with Apache avro..")
        with open(self.schema_fn, "r") as f:
            _ = avro.schema.parse(f.read())

    def validate_file(self, data_filename: str):
        schema = str | None
        with open(self.schema_fn, "r") as f:
            print(f"--> Reading schema {os.path.basename(self.schema_fn)}..")
            schema = json.load(f)

        with open(data_filename, "r", encoding="utf-8") as fo:
            print(f"--> parsing {data_filename}")
            obj = json.load(fo)
            assert fastavro_validate(obj, schema)

    def validate(self):
        self.validate_file(self.example_data_filename())


class TestProtocol(unittest.TestCase):
    def test_fastavro(self):
        pass
        schema = {"type": "record",
                  "name": "sanity",
                  "fields": [
                      {"name": "name", "type": "string"},
                      {"name": "age", "type": "int"}
                  ]
                  }

        data = {"name": "John", "age": 42}
        fastavro_validate(data, schema)

    def test_sanity(self):
        protocol = Protocol("Sanity", "0.1-example")
        protocol.validate()

    def test_protocol(self):
        # TODO auto-find all protocol files
        Protocol("TripEnd", "0.1-example").validate()
        Protocol("TripStart", "0.1-example").validate()
