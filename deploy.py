from pyinfra.operations import server, apt, ssh, pip, files, server
from pyinfra import local, logger

import os
from pathlib import Path
from textwrap import dedent
from dotenv import load_dotenv

from helpers import Video


# if __name__ == '__main__':
load_dotenv()

Video(
    filepath=Path.cwd() / "files/videos" / "meeting-2023-06-16.mov",
    remote_basepath=Path("/tmp/"),
).run()

