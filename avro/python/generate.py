import os
from pathlib import Path
import subprocess
from avrotize.avrotoproto import convert_avro_to_proto

from docs import Docs

# Main script to generate all the things from the Avro IDL definitions.


class Schemas:
    """ Helper class for enumerating schemas in this repo. Provides a
        builder-style API (methods that return reference to self to allow
        chaining calls). """

    def __init__(self):
        self.schemas: list[Path] = []
        # path to root of project
        self.project_root: Path = Path(__file__).parent.parent.parent

    # --> Buider methods

    def with_version(self, version: str) -> 'Schemas':
        return self.find_in_path(os.path.join(self.project_root, "protocol", f"v{version}"))

    def all(self) -> 'Schemas':
        return self.find_in_path()

    def find_in_path(self, path: str | None = None) -> 'Schemas':
        """ Find all Avro schemas in given `path`. If path is None, use
            top-level project default. """
        if not path:
            path = os.path.join(self.project_root, "protocol")
        start_path = Path(path)
        print(f"--> Searching for Avro schema files in {start_path}")
        self.schemas = list(start_path.rglob("*.avsc"))
        return self

    def from_avro_idl(self) -> 'Schemas':
        """ Generate all schemas from main Avro IDL files, and select all
            schemas for future operations on this object. """
        protocol_path = self.project_root / "protocol"
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


def main():

    print("--> Generating Avro schemas..")
    schemas = Schemas().from_avro_idl()
    print(f"--> Found schemas: {schemas.schemas}")

    print("--> Generating proto3 definitions for all schemas")
    schemas.gen_proto3()

    docs = Docs(schemas.project_root / "protocol")
    docs_dir = schemas.project_root / "docs" / "generated"
    docs_dir.mkdir(parents=True, exist_ok=True)
    print(f"--> Generating markdown docs in {docs_dir}")
    docs.generate_markdown(docs_dir)


if __name__ == "__main__":
    main()
