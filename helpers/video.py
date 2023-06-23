
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

from .infra import get_many, install_pip_dependencies, put_many, server_shell

class Scripts(str, Enum):
    transcribe = "scripts/transcribe.py"
    generate = "scripts/generate.py"

    @classmethod
    def put_in_remote(cls, remote_basepath: Path) -> dict[Path, Path]:
        filepaths = {s.value: remote_basepath / s.value for s in cls}
        put_many(filepaths)
        return filepaths

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
    
    def _get_property_filepath(self, name: str, suffix: str) -> Path:
        # return self.filepath.parent / dir / self.filepath.with_suffix(suffix).name
        directory = self.filepath.parent / self.filepath.stem
        directory.mkdir(exist_ok=True)
        return (directory / name).with_suffix(suffix)

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
        prompt = dedent("""'
        # UTML Meeting

        ## Transcription
        Here is the transcription of our last meeting:
            
        {text}

        ## Topics

        In this meeting we discussed the following topics:
        -'""").strip()

        self._call_script(Scripts.generate, prompt=prompt, filepath=self.remote.transcription, output=self.remote.summary, max_output_new_tokens=2048)

    def _describe(self):
        prompt = dedent("""'
        # UTML Meeting

        ## Topics

        In this meeting we discussed the following topics:

        {text}

        ## TL;DR

        Meeting summary in 100 words:
        '""").strip()
        self._call_script(Scripts.generate, prompt=prompt, filepath=self.remote.summary, output=self.remote.description, max_output_new_tokens=256)

    def _get_all(self):
        get_many({
            self.remote.transcription: self.transcription,
            self.remote.summary: self.summary,
            self.remote.description: self.description,
        })

    def _authorize(self):
        cli = Client(client_id=os.getenv("YOUTUBE_CLIENT_ID"), client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"))
        print(cli.get_authorize_url())
        cli.generate_access_token(authorization_response=input("Enter the url: "))
        return cli

    def _upload(self):
        cli = self._authorize()
        creation_time = self.creation_time.strftime("%Y/%m/%d")

        body = Video(
            snippet=VideoSnippet(
                title=f"UTML Meeting {creation_time}",
                description=self.description.read_text(),
                # TODO: description from LLM
                # TODO: thumbnails=Thumbnails()
                # TODO: captions (Whisper)
                # TODO: translated captions
                # TODO: dubbing (AI)
                # TODO: auto editing (5min)
            )
        )

        media = Media(filename=self.filepath)

        upload = cli.videos.insert(
            body=body,
            media=media,
            parts=["snippet"],
            notify_subscribers=True
        )

        video_body = None
        while video_body is None:
            status, video_body = upload.next_chunk()
            if status:
                print(f"Upload progress: {status.progress()}")


    def run(self) -> None:
        self._extract_audio()

        # prepare remote environment
        apt.packages(
            name="Install APT dependencies",
            packages=["build-essential"],
            # update=True,
        )

        self.scripts = Scripts.put_in_remote(self.remote_basepath)
        self.python = install_pip_dependencies(venv=os.environ["VENV_PATH"])
        put_many({self.audio: self.remote.audio})

        # run scripts
        self._transcribe()
        self._summarize()
        self._describe()     

        # download results
        self._get_all()   

        # upload to youtube
        # self._upload()

        