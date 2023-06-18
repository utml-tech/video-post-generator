import os
from pathlib import Path
from textwrap import dedent
from dotenv import load_dotenv
from pyyoutube import Client
from pyyoutube.models import Video, VideoSnippet, Thumbnails
from pyyoutube.media import Media



if __name__ == '__main__':
    load_dotenv()

    cli = Client(client_id=os.getenv("YOUTUBE_CLIENT_ID"), client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"))
    print(cli.get_authorize_url())
    cli.generate_access_token(authorization_response=input("Enter the url: "))
    # response = "https://localhost/?state=Python-YouTube&code=4/0AbUR2VN3-ilFMDguxsC2amBtXvQrQ4dBzz8AKpxKHvDWJ6manaBt3ltjSyqvQnmBUlCCQw&scope=profile%20https://www.googleapis.com/auth/youtube%20https://www.googleapis.com/auth/userinfo.profile"
    # cli.generate_access_token(authorization_response=response)

    channels_list = cli.channels.list(mine=True)

    body = Video(
        snippet=VideoSnippet(
            title="Test video",
            description=dedent("""
                This is a test video upload.
            """),
            # TODO: thumbnails=Thumbnails()
            # TODO: captions (Whisper)
            # TODO: tranlated captions
            # TODO: dubbing (AI)
            # TODO: auto editing (5min)
        )
    )

    media = Media(filename=Path.cwd() / "files/videos/test.mov")

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




