# video-post-generator

Transforms a video input into a proper blog post

## General Algorithm

1. get video
2. extract audio file
3. send audio file to server via ssh (remote)
4. get full transcript from audio (remote)
5. get subtitles .srt file from audio (remote)
6. summarize transcript with LLM (remote)
7. upload video to youtube with subtitles and thumbnail
8. create .md post with youtube link, summary, and transcript
9. open PR adding .md file to website repo (jinja2)

## references

- https://github.com/FreedomIntelligence/LLMZoo
- https://github.com/Hannibal046/Awesome-LLM
- https://github.com/openai/whisper
- https://github.com/guillaumekln/faster-whisper
- https://sns-sdks.lkhardy.cn/python-youtube/usage/work-with-client/#insert

## transcription

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

### fastchat

[t5](https://github.com/lm-sys/FastChat#fastchat-t5)

```bash
python3 -m fastchat.serve.cli --model-path lmsys/fastchat-t5-3b-v1.0 --style rich --num-gpus 3 --load-8bit
```

### llama

#### install

```bash
curl -o- https://raw.githubusercontent.com/shawwn/llama-dl/56f50b96072f42fb2520b1ad5a1d6ef30351f23c/llama.sh | bash
```

CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python

```bash
python -m transformers.models.llama.convert_llama_weights_to_hf \
    --input_dir llama/ --model_size 7B --output_dir llama/hf/
```

```bash
python3 -m fastchat.model.apply_delta \
    --base-model-path llama/7B/ \
    --target-model-path /vicuna/7B/ \
    --delta-path lmsys/vicuna-7b-delta-v1.1
```

```bash
python3 -m llama.inference --ckpt_dir files/llama/7B --tokenizer_path files/llama/tokenizer.model
```