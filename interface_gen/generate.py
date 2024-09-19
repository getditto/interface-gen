import argparse
import os
from pathlib import Path
import subprocess
from avrotize.avrotoproto import convert_avro_to_proto, json

from . import docs
from . import toolchain

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

    def __init__(self, protocol_dir: Path | str):
        self.schemas: list[Path] = []
        # path to root of protocol directory
        self.proto_dir = Path(protocol_dir)

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

    def from_avro_idl(self, env: dict[str, str], avro_cmd: list[str],
                      output_dir: Path) -> 'Schemas':
        """ Generate all schemas from main Avro IDL files, and select all
            schemas for future operations on this object. """
        protocol_path = self.proto_dir
        avdl_files = protocol_path.rglob("*.avdl")
        for avdl in avdl_files:
            print(f"--> Generating schema(s) for {avdl}")
            version_dir = avdl.parent.name
            sdir = output_dir / version_dir / "schema"
            subprocess.check_call(avro_cmd + [str(avdl), str(sdir)], env=env)
        return self.find_in_path(str(output_dir))

    # --> Action methods

    def gen_proto3(self):
        for schema_file in self.schemas:
            pp = Path(schema_file)
            pb_dir = pp.parent.parent / "proto3"
            pb_dir.mkdir(parents=True, exist_ok=True)
            print(f"--> Generating proto3 for {str(schema_file)} in {pb_dir}")
            convert_avro_to_proto(schema_file, pb_dir)
            # workaround: avrotize func. above always names file
            # <namespace>.proto, which causes all except the last schema to be
            # overwritten. Rename that
            #  output file here, until we can fix the avrotize lib.
            ns = namespace(schema_file)
            if ns:
                proto_file = pb_dir / f"{ns}.proto"
                new_file = pb_dir / f"{schema_file.stem}.proto"
                proto_file.rename(new_file)


def main():
    epilog = """Note:
Assumes your protocol directory (-p) contains subfolders named 'v<version>'
where <version> is an arbitrary version string. Within each of these version
directories, you should have your Avro IDL (.avdl) files.

Output will be written to the output directory (-o): Avro schemas, proto3
definitions, markdown documentation.
"""
    desc = "Generate docs and definitions from Avro IDL."
    parser = argparse.ArgumentParser(prog="generate.py", description=desc,
                                     epilog=epilog)
    parser.add_argument('-p', '--protocol-dir',
                        help="Path w/ Avro IDL files in version subdirs")
    parser.add_argument('-o', '--output-dir', required=True,
                        help="Path where to generate markdown docs")
    parser.add_argument('-i', '--install-toolchain',
                        help="(deprecated: always attempts toolchain install)",
                        action="store_true")
    args = parser.parse_args()

    (env, avro_cmd) = toolchain.install()

    if args.protocol_dir:
        proto_dir = Path(args.protocol_dir)
    else:
        proto_dir = Path(__file__).parent.parent.parent / "protocol"

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = proto_dir.parent / "generated"

    print("--> Generating Avro schemas..")
    schemas = Schemas(proto_dir).from_avro_idl(env, avro_cmd, out_dir)
    print(f"--> Found schemas: {schemas.schemas}")

    print("--> Generating proto3 definitions for all schemas")
    schemas.gen_proto3()

    docgen = docs.Docs(schemas.proto_dir, Path(args.output_dir))
    docs_dir = out_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    print(f"--> Generating markdown docs in {docs_dir}")
    docgen.generate_markdown(docs_dir)


if __name__ == "__main__":
    main()
