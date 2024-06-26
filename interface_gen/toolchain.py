import jdk
from pathlib import Path
import subprocess
import shutil

AVRO_VERSION = "1.11.3"


def script_dir() -> Path:
    return Path(__file__).parent


def download_file(url: str, out_dir: Path):
    command = f"curl -OL {url}"
    print(f"--> Downloading {url} to {out_dir}")
    subprocess.run(command, cwd=out_dir, shell=True, check=True)


def avro_jar(version: str) -> Path:
    return Path(f"avro-tools-{version}.jar")


def ensure_jre():
    """ Ensure that JRE is installed. """
    # See if jdk / jre already installedd
    jre = shutil.which('java')
    if jre:
        print(f"(Java is already installed: {jre})")
        return

    print("--> Installing OpenJDK 22 in $HOME/.jre/")
    jdk.install('22', jre=True)


def install_avro_tools(target_dir: Path):
    global AVRO_VERSION
    target_dir.mkdir(parents=True, exist_ok=True)
    jar = avro_jar(AVRO_VERSION)
    jarpath = target_dir / jar
    if jarpath.exists():
        print(f"(Avro tools already installed: {jarpath})")
    else:
        url = f"https://dlcdn.apache.org/avro/avro-{AVRO_VERSION}/java/{jar}"
        download_file(url, target_dir)


def create_avro_script(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    script = target_dir / "avro-idl.sh"
    print(f"--> Generating IDL->Schema script {script}")
    with script.open("w") as f:
        f.write(f"""\
#!/bin/bash

# This script is generated by toolchain.py
java -jar {target_dir}/{avro_jar(AVRO_VERSION)} idl2schemata "$@"
""")
    script.chmod(0o755)


def install():
    """ Install the toolchain: tools needed for build and code generation. """
    sdir = script_dir()
    avro_bin = sdir.parent / "avro" / "bin"

    ensure_jre()
    install_avro_tools(avro_bin)
    create_avro_script(avro_bin)
