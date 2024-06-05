import argparse
import os
from pathlib import Path
import subprocess
from avrotize.avrotoproto import convert_avro_to_proto, json

from docs import Docs

# Main script to generate all the things from the Avro IDL definitions.


def namespace(schema_file: Path) -> str | None:
    """ Extract namespace from Avro schema file. """
    with open(schema_file, "r") as f:
        obj = json.load(f)
        return obj.get("namespace", None)


class Schemas:
    """ Helper class for enumerating schemas in this repo. Provides a
        builder-style API (methods that return reference to self to allow
        chaining calls). """

    def __init__(self, protocol_dir: str | None = None):
        self.schemas: list[Path] = []
        # path to root of protocol directory
        if protocol_dir:
            self.proto_dir = Path(protocol_dir)
        else:
            self.proto_dir = Path(__file__).parent.parent.parent / "protocol"

    # --> Buider methods

    def with_version(self, version: str) -> 'Schemas':
        return self.find_in_path(os.path.join(self.proto_dir, f"v{version}"))

    def all(self) -> 'Schemas':
        return self.find_in_path()

    def find_in_path(self, path: str | None = None) -> 'Schemas':
        """ Find all Avro schemas in given `path`. If path is None, use
            top-level project default. """
        if path:
            start_path = Path(path)
        else:
            start_path = self.proto_dir
        print(f"--> Searching for Avro schema files in {start_path}")
        self.schemas = list(start_path.rglob("*.avsc"))
        return self

    def from_avro_idl(self) -> 'Schemas':
        """ Generate all schemas from main Avro IDL files, and select all
            schemas for future operations on this object. """
        protocol_path = self.proto_dir
        avdl_files = protocol_path.rglob("*.avdl")
        for avdl in avdl_files:
            print(f"--> Generating schema(s) for {avdl}")
            subprocess.check_call(["avro/bin/avro-idl.sh", avdl, avdl.parent / "schema"])
        return self.all()

    # --> Action methods

    def gen_proto3(self):
        for schema_file in self.schemas:
            pp = Path(schema_file)
            proto_dir = pp.parent.parent / "proto3"
            print(f"--> Generating proto3 for {schema_file.stem} in {proto_dir}")
            convert_avro_to_proto(schema_file, proto_dir)
            # workaround: avrotize func. above always names file <namespace>.proto,
            #  which causes all except the last schema to be overwritten. Rename that
            #  output file here, until we can fix the avrotize lib.
            ns = namespace(schema_file)
            if ns:
                proto_file = proto_dir / f"{ns}.proto"
                new_file = proto_dir / f"{schema_file.stem}.proto"
                proto_file.rename(new_file)


def main():
    epilog = """Note:
Assumes your protocol directory (-p) contains subfolders named 'v<version>'
where <version> is an arbitrary version string. Within each of these version
directories, you should have your Avro IDL (.avdl) files.

This script will generate Avro schemas from the IDL files, and then generate
proto3 definitions, etc..

Finally, it will generate markdown documentation at in the docs directory (-d).
"""
    parser = argparse.ArgumentParser(prog="generate.py",
                                     description="Generate docs and definitions from Avro IDL.",
                                     epilog=epilog)
    parser.add_argument('-p', '--protocol-dir',
                        help="Path where your version subdirs with Avro IDL files live")
    parser.add_argument('-d', '--docs-dir',
                        help="Path where to generate markdown docs")
    args = parser.parse_args()

    print("--> Generating Avro schemas..")
    schemas = Schemas(args.protocol_dir).from_avro_idl()
    print(f"--> Found schemas: {schemas.schemas}")

    print("--> Generating proto3 definitions for all schemas")
    schemas.gen_proto3()

    docs = Docs(schemas.proto_dir)
    if args.docs_dir:
        docs_dir = Path(args.docs_dir)
    else:
        docs_dir = schemas.proto_dir.parent / "docs" / "generated"
    docs_dir.mkdir(parents=True, exist_ok=True)
    print(f"--> Generating markdown docs in {docs_dir}")
    docs.generate_markdown(docs_dir)


if __name__ == "__main__":
    main()
