from dataclasses import dataclass
from pathlib import Path, PurePath
import re


@dataclass
class Schema:
    name: str
    path: Path

    def raw_proto3(self) -> str:
        proto3_dir = self.path.parent.parent / "proto3"
        proto3_file = proto3_dir / f"{self.name}.proto"
        with proto3_file.open("r") as f:
            return f.read()


@dataclass
class Protocol:
    name: str
    path: Path
    schemas: list[Schema]

    # Currently only using enums and records, each of which generate their own
    # .avsc schema.
    type_re = re.compile(r"\s*(?:enum|record)\s+([a-zA-Z0-9_]+)\s*{")

    @classmethod
    def from_avdl(cls, avdl_path: Path, gen_path: Path) -> 'Protocol':
        _schemas: list[Schema] = []
        with avdl_path.open("r") as f:
            for line in f:
                match = cls.type_re.match(line)
                if match:
                    schema_name = match.group(1)
                    version = avdl_path.parent.name
                    schema_path = gen_path / version / "schema" / f"{schema_name}.avsc"
                    if not schema_path.exists():
                        print(f"Error: Expected schema file {schema_path} not found")
                    _schemas.append(Schema(schema_name, schema_path))
        return cls(avdl_path.stem, avdl_path, _schemas)

    def raw_text(self) -> str:
        with self.path.open("r") as f:
            return f.read()


@dataclass
class Version:
    version: str
    path: PurePath
    protocols: list[Protocol]


def h1(title: str) -> str:
    return f"# {title}\n\n"


def h2(title: str) -> str:
    return f"## {title}\n\n"


def h3(title: str) -> str:
    return f"### {title}\n\n"


def h4(title: str) -> str:
    return f"#### {title}\n\n"


def list_item(text: str, indent=0) -> str:
    indent = ' ' * (2*indent)
    return f'{indent}- {text}\n'


def link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def to_anchor(text: str) -> str:
    text = text.replace("(", "").replace(")", "")
    return "#" + text.lower().replace(" ", "-")


def code(text: str, type='') -> str:
    s = f"```{type}\n"
    s += text + "\n"
    s += "```\n\n"
    return s


class Docs:
    """ Basic documentation generation for Avro IDL types and their
        derivations. """

    def __init__(self, input_path: Path, gen_path: Path):
        self.root_path = input_path  # where source .avdl files live
        self.gen_path = gen_path    # where generated .avsc files live
        self.versions: list[Version] = []
        self._enumerate()

    # Create a dictionary describing the overall documentation structure:
    # Version -> Protocol -> Schema (link to file, protoc)
    # Create a file for each version.
    # Each file starts with a table of contents with links to sections.
    # Each IDL "protocol" has a section that (ideally) contains the schemas
    # generated from that protocol.
    # Each schema has links to the corresponding proto3 definition, and any
    # other code or IDLs generated from the schema.

    def _enumerate(self):
        self.versions: list[Version] = []
        version_dirs = self.root_path.glob("*")
        for vdir in version_dirs:
            avdl_files = vdir.glob("*.avdl")
            protos = []
            for avdl in avdl_files:
                protocol = Protocol.from_avdl(avdl, self.gen_path)
                protos.append(protocol)
            v = Version(vdir.name, vdir, protos)
            self.versions.append(v)

    def generate_index(self, output_dir: Path):
        index_path = output_dir / "index.md"
        with index_path.open("w") as f:
            f.write(h1("Interface Specification Versions"))
            for ver in self.versions:
                f.write(list_item(link(ver.version, f"version-{ver.version}.md")))

    def generate_versions(self, output_dir: Path, proto_url_path: str):
        # loop through versions, writing the table of contents while building
        # up the body of the document
        for ver in self.versions:
            ver_path = output_dir / f"version-{ver.version}.md"
            body = ""
            protoc_body = ""
            with ver_path.open("w") as f:
                f.write(h1(f"Interface Specification Version {ver.version}"))
                f.write(h2("Overview"))
                f.write("Table of schemas, grouped by protocol:\n\n")
                for proto in ver.protocols:
                    href = link(proto.name + " (Avro IDL)", to_anchor(proto.name))
                    p3_section = proto.name + " (proto3)"
                    p3_href = link("protobuf", to_anchor(p3_section))
                    f.write(list_item(f"{href} (see also {p3_href}):"))

                    body += h3(proto.name)
                    body += f"See also the {p3_href}\n\n"
                    protoc_body += h3(p3_section)

                    # Print table of contents by protocol
                    for schema in proto.schemas:
                        spath = Path(proto_url_path) / f"v{ver.version}"
                        spath = spath / "schema" / schema.path.name
                        li = list_item(link(schema.name, str(spath)), indent=1)
                        f.write(li)

                        p3_name = schema.name + " (proto3)"
                        protoc_body += h4(p3_name)
                        protoc_body += code(schema.raw_proto3(), type='protobuf')

                    body += code(proto.raw_text(), type='avdl')

                f.write(h2("Protocols"))
                f.write(body)

                f.write(h2("Proto3 Definitions"))
                f.write(protoc_body)

    def generate_markdown(self, output_dir: Path):
        self.generate_index(output_dir)
        self.generate_versions(output_dir, "/protocol")
