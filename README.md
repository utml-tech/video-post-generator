# video-post-generator

Transforms a video input into a proper blog post

## functions

1. upload to youtube
2. write transcript
3. post on website (open PR)

### transcription

- uses Whisper model
- uses LLM to fix mistakes and make summary

### commands

1. extract audio: `ffmpeg -i files/videos/demo.mov -vn -acodec copy /tmp/files/output-audio.aac`
2. get transcription: `whisper /tmp/files/output-audio.aac --model medium`

whisper /tmp/files/output-audio.aac --model medium --task transcribe --verbose false \
                                    --output_dir outputs --output_format all \
                                    --language en \
                                    --initial_prompt file name \
                                    --word_timestamps true \
                                    --threads 8


