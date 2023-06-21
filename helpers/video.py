
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path

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

from .infra import install_pip_dependencies, put_many, server_shell

class Scripts(str, Enum):
    transcribe = "scripts/transcribe.py"
    summarize = "scripts/summarize.py"

    @classmethod
    def put_in_remote(cls, remote_basepath: Path) -> dict[str, Path]:
        new_paths = put_many([s.value for s in cls], remote_basepath)
        return dict(zip(cls, new_paths))

@dataclass
class Video:
    filepath: Path
    remote_basepath: Path = Path("/tmp/")

    @cached_property
    def metadata(self) -> dict:
        return ffmpeg.probe(self.filepath)
    
    @property
    def creation_time(self) -> datetime:
        t = self.metadata["format"]["tags"]["creation_time"]
        return datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def audio(self) -> Path:
        return self._get_property_filepath("audio", ".aac")

    @property
    def transcription(self) -> Path:
        return self._get_property_filepath("transcriptions", ".txt")
    
    @property
    def subtitles(self) -> Path:
        return self._get_property_filepath("subtitles", ".srt")
    
    @property
    def description(self) -> Path:
        return self._get_property_filepath("descriptions", ".txt")
    
    @property
    def summary(self) -> Path:
        return self._get_property_filepath("summaries", ".txt")

    @property
    def post(self) -> Path:
        return self._get_property_filepath("posts", ".md")

    @property
    def remote(self) -> Video:
        return Video(self.remote_basepath / self.filepath.name)
    
    def _get_property_filepath(self, dir: str, suffix: str) -> Path:
        return self.filepath.parent / dir / self.filepath.with_suffix(suffix).name
    
    def _prepare_remote(self) -> None:
        self.scripts = Scripts.put_in_remote(self.remote_basepath)
        self.python = install_pip_dependencies(venv=os.environ["VENV_PATH"])

        put_many([self.audio], self.remote_basepath)

    def _extract_audio(self) -> None:
        if self.audio.exists():
            logger.debug(f'audio file already exists {self.audio}')
            return 

        logger.debug(f'extracting audio from {self.filepath}')
        local.shell(f'ffmpeg -i {self.filepath} -vn -acodec copy {self.audio}')

    def _call_script(self, script: Scripts, **kwargs) -> None:
        kwargs = " ".join([f"--{k} {v}" for k, v in kwargs.items()])
        server.shell(f"{self.python} {self.scripts[script]} {kwargs}")

    def _transcribe(self):
        self._call_script(Scripts.transcribe, filepath=self.remote.audio, output=self.remote.transcription)
        
    def _summarize(self):
        self._call_script(Scripts.summarize, filepath=self.remote.transcription, output=self.remote.summary)

    def _describe(self):
        self._call_script(Scripts.describe, filepath=self.remote.summary, output=self.remote.description)

    def _get_all(self):
        get_many({
            self.remote.transcription: self.transcription,
            self.remote.summary: self.summary,
            self.remote.description: self.description,
        })

        