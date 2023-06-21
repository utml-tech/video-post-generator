from pyinfra.operations import server, apt, ssh, pip, files, server
from pyinfra import local, logger

import os
from pathlib import Path
from textwrap import dedent
from dotenv import load_dotenv
from pyyoutube import Client
from pyyoutube.models import Video, VideoSnippet, Thumbnails
from pyyoutube.media import Media

from datetime import datetime

import ffmpeg

from pathlib import Path

from helpers import put_many, install_pip_dependencies

def extract_audio_from_video(filepath: Path) -> Path:
    audio_path = filepath.with_suffix(".aac")

    if audio_path.exists():
        logger.info(f'audio file already exists {audio_path}')
        return audio_path

    logger.info(f'extracting audio from {filepath}')
    local.shell(f'ffmpeg -i {filepath} -vn -acodec copy {audio_path}')

    logger.info(f'extracted audio to {audio_path}')
    return audio_path

def transcribe_audio(filepath: Path, python: Path, remote_basepath = Path("/tmp/"), output = Path.cwd() / "files" / "transcriptions" / "output.txt") -> None:
    logger.info('uploading files to remote server')
    remote_input, script = put_many([filepath, "scripts/transcribe.py"], remote_basepath)

    remote_output =  remote_basepath / filepath.with_suffix(".txt").name
    logger.info(f'transcribing audio from {remote_input}')
    server.shell(f"{python} {script} --filepath {remote_input} --output {remote_output}")

    files.get(
        name="Download transcription",
        src=str(remote_output),
        dest=str(output),
    )

def summarize_transcription(transcription: Path, output: Path) -> None:
    # https://github.com/microsoft/guidance
    logger.info(f'summarizing transcription {transcription}')


load_dotenv()
videofile = Path.cwd() / "files/videos/meeting-2023-06-16.mov"



breakpoint()

venv = Path("/home/pedro/venv")
python = install_pip_dependencies(venv)

audiofile = extract_audio_from_video(videofile)
transcribe_audio(audiofile, python)

# pyinfra cv6 scripts/deploy.py

# hosts = ["@dockerssh/dl02:pytorch/pytorch:1.5.1-cuda10.1-cudnn7-devel"]

# hosts = [
#     ("ssh.recod.ic.unicamp.br", {
#         'ssh_hostname': 'ssh.recod.ic.unicamp.br',
#         'ssh_user': 'pvaloi',
#         'ssh_key': None,
#         'ssh_password': '3bUL7ss3@9n*}SCB'
#     })
# ]

# extract audio
