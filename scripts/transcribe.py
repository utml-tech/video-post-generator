from __future__ import annotations

import os
from pathlib import Path

import fire

from tqdm import tqdm

import torch
from faster_whisper import WhisperModel


def transcribe(
        filepath: str,
        output: str,
        model: str = "large-v2",
        compute_type: str = "int8_float16",
        language: str | None = None,
        num_threads: int | None = None,
        num_devices: int | None = None,
        force: bool = False,
):
    if not force and Path(output).exists():
        print(f"File {output} already exists. Skipping.")
        return

    num_threads = num_threads or os.cpu_count() // 2
    num_devices = num_devices or torch.cuda.device_count()

    model = WhisperModel(
        model_size_or_path=model, 
        device="cuda", 
        compute_type=compute_type, 
        device_index=list(range(num_devices)),
        cpu_threads=num_threads,
        num_workers=num_threads
    )

    segments, info = model.transcribe(
        audio=filepath, 
        language=language,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,  # filter out parts without speech
        # initial_prompt="a talk about using stable diffusion to build anime videos"
    )

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    transcription = "\n".join([s.text for s in segments])
    Path(output).write_text(transcription)

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

if __name__ == '__main__':
  fire.Fire(transcribe)