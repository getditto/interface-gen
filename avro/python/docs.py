from dataclasses import dataclass
from pathlib import Path, PurePath
import re


@dataclass
class Schema:
    name: str
    path: PurePath


@dataclass
class Protocol:
    name: str
    path: Path
    schemas: list[Schema]

    # Currently only using enums and records, each of which generate their own
    # .avsc schema.
    type_re = re.compile(r"\s*(?:enum|record)\s+([a-zA-Z0-9_]+)\s*{")

    @classmethod
    def from_avdl(cls, avdl_path: Path) -> 'Protocol':
        _schemas: list[Schema] = []
        with avdl_path.open("r") as f:
            for line in f:
                match = cls.type_re.match(line)
                if match:
                    schema_name = match.group(1)
                    schema_path = avdl_path.parent / "schema" / f"{schema_name}.avsc"
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


def list_item(text: str, indent=0) -> str:
    indent = ' ' * (2*indent)
    return f'{indent}- {text}\n'


def link(text: str, url: str) -> str:
    return f"[{text}]({url})"


def to_anchor(text: str) -> str:
    return "#" + text.lower().replace(" ", "-")


def code(text: str, type='') -> str:
    s = f"```{type}\n"
    s += text + "\n"
    s += "```\n"
    return s


class Docs:
    """ Basic documentation generation for Avro IDL types and their
        derivations. """

    def __init__(self, root_path: Path):
        self.root_path = root_path
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
        version_dirs = self.root_path.glob("v*")
        for vdir in version_dirs:
            vname = vdir.name[1:]  # strip leading 'v'
            avdl_files = vdir.glob("*.avdl")
            protos = []
            for avdl in avdl_files:
                protocol = Protocol.from_avdl(avdl)
                protos.append(protocol)
            self.versions.append(Version(vname, vdir, protos))

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
            with ver_path.open("w") as f:
                f.write(h1(f"Interface Specification Version {ver.version}"))
                f.write(h2("Overview"))
                for proto in ver.protocols:
                    sum = f"{link(proto.name, to_anchor(proto.name))} includes schemas:"
                    f.write(list_item(sum))
                    for schema in proto.schemas:
                        spath = Path(proto_url_path) / f"v{ver.version}"
                        spath = spath / "schema" / schema.path.name
                        f.write(list_item(link(schema.name, str(spath)), indent=1))
                    body += h3(proto.name)
                    body += code(proto.raw_text(), type='avdl')

                f.write(h2("Protocols"))
                f.write(body)

    def generate_markdown(self, output_dir: Path):
        self.generate_index(output_dir)
        self.generate_versions(output_dir, "/protocol")
