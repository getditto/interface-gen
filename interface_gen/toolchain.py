import jdk
import os
from pathlib import Path
import subprocess
import shutil

AVRO_VERSION = "1.12.0"


def script_dir() -> Path:
    return Path(__file__).parent


def download_file(url: str, out_dir: Path):
    command = f"curl -OL {url}"
    print(f"--> Downloading {url} to {out_dir}")
    subprocess.run(command, cwd=out_dir, shell=True, check=True)


def avro_jar(version: str) -> Path:
    return Path(f"avro-tools-{version}.jar")


def find_java(root: Path) -> Path | None:
    java_files = list(root.rglob("java"))
    if len(java_files) == 0:
        print(f"Java not found in {str(root)}")
        return None
    print(f"found java: {list(map(lambda p: str(p), java_files))}")
    java_path = Path(java_files[0])
    env = java_env(java_path)
    subprocess.check_output([str(java_path), '-version'], env=env)
    return java_path


def ensure_jre() -> Path | None:
    """ Ensure that JRE is installed, and return its path. """
    jre_dir = Path.home() / '.jre'
    # See if jdk / jre already installedd
    jre = shutil.which('java')
    if not jre:
        jre = find_java(jre_dir)
    if jre:
        print(f"(Java is already installed: {jre})")
        return Path(jre)

    print(f"--> Installing OpenJDK 22 in {jre_dir}")
    jdk.install('22', jre=True)

    return find_java(jre_dir)


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


def java_env(java_path: Path) -> dict[str, str]:
    """ Return environment with path, etc. set for java command """
    bin_dir = java_path.parent
    java_home = bin_dir.parent
    lib_dir = java_home / 'lib'
    new_path = os.environ['PATH'] + f":{bin_dir}"
    env = os.environ.copy()
    env['PATH'] = new_path
    env['LD_LIBRARY_PATH'] = str(lib_dir)
    return env


# TODO make this file a class that retains toolchain paths, etc. and provides a
# method to run the command
def create_avro_cmd(java_path: Path, target_dir: Path) \
        -> tuple[dict[str, str], list[str]]:
    env = java_env(java_path)
    return (env, [str(java_path), '-jar',
                  f'{target_dir}/{avro_jar(AVRO_VERSION)}',
                  'idl2schemata'])


def install() -> tuple[dict[str, str], list[str]]:
    """ Install the toolchain and return the command needed to generate
        schemas and code. """
    sdir = script_dir()
    avro_bin = sdir.parent / "avro" / "bin"

    java_path = ensure_jre()
    if not java_path:
        raise Exception("Failed to install java.")
    install_avro_tools(avro_bin)
    return create_avro_cmd(java_path, avro_bin)
