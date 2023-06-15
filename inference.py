from textwrap import dedent
import torch

import json
from pathlib import Path
from llama import ModelArgs, Transformer, Tokenizer, LLaMA


def load(
    ckpt_dir: str,
    tokenizer_path: str,
    local_rank: int,
    world_size: int,
    max_seq_len: int,
    max_batch_size: int,
) -> LLaMA:
    checkpoints = sorted(Path(ckpt_dir).glob("*.pth"))
    assert world_size == len(
        checkpoints
    ), f"Loading a checkpoint for MP={len(checkpoints)} but world size is {world_size}"
    ckpt_path = checkpoints[local_rank]

    checkpoint = torch.load(ckpt_path, map_location="cpu")

    with open(Path(ckpt_dir) / "params.json", "r") as f:
        params = json.loads(f.read())

    model_args: ModelArgs = ModelArgs(
        max_seq_len=max_seq_len, max_batch_size=max_batch_size, **params
    )
    tokenizer = Tokenizer(model_path=tokenizer_path)
    model_args.vocab_size = tokenizer.n_words
    torch.set_default_tensor_type(torch.cuda.HalfTensor)
    model = Transformer(model_args)
    torch.set_default_tensor_type(torch.FloatTensor)
    model.load_state_dict(checkpoint, strict=False)
    generator = LLaMA(model, tokenizer)
    return generator


def run(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.8,
    top_p: float = 0.95,
    max_seq_len: int = 1024,
    max_batch_size: int = 1,
):
    local_rank = 0
    world_size = 1
    generator = load(
        ckpt_dir, tokenizer_path, local_rank, world_size, max_seq_len, max_batch_size
    )
    prompts = [
        # For these prompts, the expected answer is the natural continuation of the prompt
        dedent("""Given the text below, the best possible summarization is:
        
        'it got really crazy it has no idea what is this like it's interesting like the
        the base stable diffusion is kind of crazy isn't it is this crazy results
        oh is it finished I think it finished yeah you can see here also Vivo provides
        prunes so anyway yeah you see I went back to two gigabytes it's still
        downloading
        actually one thing that I forgot is that I started by cloning the
        on this thing right
        yes I can this thing then I see the in this folder just to remember all my
        stuff like a clone.cd okay it downloaded so if it downloaded now I can just click
        here and you have to say this next and then let's just try the the hellboy'
        """)
    ]
    while True:
        print("Prompt:", prompts)
        results = generator.generate(
            prompts, max_gen_len=256, temperature=temperature, top_p=top_p
        )
        for result in results:
            print("🦙LLaMA:", result.strip())

        user_input = input("please enter your prompts (Ctrl+C to exit): ")
        prompts = [user_input]


def get_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt_dir", type=str, default="/llama_data/7B")
    parser.add_argument(
        "--tokenizer_path", type=str, default="/llama_data/tokenizer.model"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    run(
        ckpt_dir=args.ckpt_dir,
        tokenizer_path=args.tokenizer_path,
        temperature=0.8,
        top_p=0.95,
        max_seq_len=1024,
        max_batch_size=1,
    )