import os
from pathlib import Path

from faster_whisper import WhisperModel
import torch

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

num_threads = os.cpu_count() // 2

# or run on GPU with INT8
model = WhisperModel(
    model_size_or_path="large-v2", 
    device="cuda", 
    compute_type="int8_float16", 
    device_index=list(range(torch.cuda.device_count())),
    cpu_threads=num_threads,
    num_workers=num_threads
)
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe(
    audio="files/audio/audio.aac", 
    language="en",
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,  # filter out parts without speech
    # initial_prompt="a talk about using stable diffusion to build anime videos"
)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

text = "\n".join([s.text for s in segments])

filepath = Path.cwd() / "files" / "transcripts" / "output.txt"
filepath.write_text(text)


# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))