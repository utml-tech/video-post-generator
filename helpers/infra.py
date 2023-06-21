import os
from textwrap import dedent
from pyinfra.operations import files, pip, server
from pyinfra import local, logger

from pathlib import Path

def server_shell(cmd: str):
    return server.shell(dedent(cmd).replace("\n", " ").strip())

def put_many(filepaths: list[Path], remote_basepath: Path) -> None:
    filepaths = list(map(Path, filepaths))
    remote_paths = [remote_basepath / filepath.name for filepath in filepaths]

    for local, remote in zip(filepaths, remote_paths):
        files.put(
            name=f"Upload {local} to remote {remote}",
            src=str(local), 
            dest=str(remote), 
            user=os.environ["USER_ID"], 
            group=os.environ["GROUP_ID"], 
            mode=None, 
            add_deploy_dir=True, 
            create_remote_dir=True,
            force=False, 
            assume_exists=False,
        )

    return remote_paths

def install_pip_dependencies(venv: str, requirements = Path.cwd() / "requirements.txt") -> None:
    python = Path(venv) / "bin" / "python"

    pip.venv(
        name="Create a virtualenv",
        path=venv,
        present=True,
        site_packages=True,
    )

    server.shell(f"{python} -m pip install -U pip")

    pip.packages(
        name="Install audio transcription dependencies",
        packages=requirements.read_text().splitlines(),
        present=True,
        latest=True,
        pip="pip",
        virtualenv=venv,
        virtualenv_kwargs=dict(present=True),
    )

    logger.info('installing pip dependencies')

    return python