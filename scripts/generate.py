from pathlib import Path
import torch
import transformers
from transformers import AutoTokenizer
from transformers import pipeline
import fire

DTYPE = torch.bfloat16

def generate(
    prompt: str, # 'Here is a recipe for vegan banana bread:\n', 
    output: str | None = None, 
    model_name: str = "mosaicml/mpt-7b-storywriter",
    tokenizer: str = "EleutherAI/gpt-neox-20b",
    max_seq_len: int = 65536,
    max_output_new_tokens: int = 128,
):
    """text generation
    
    references:
        https://www.mosaicml.com/blog/mpt-7b
        https://huggingface.co/mosaicml/mpt-7b-storywriter
    """
    config = transformers.AutoConfig.from_pretrained(model_name, trust_remote_code=True)
    config.attn_config['attn_impl'] = 'triton'
    config.init_device = 'cuda:0' # For fast initialization directly on GPU!
    config.max_seq_len = max_seq_len # (input + output) tokens can now be up to 83968

    model = transformers.AutoModelForCausalLM.from_pretrained(model_name, config=config, torch_dtype=DTYPE, trust_remote_code=True)
    # TODO: model = BetterTransformer.transform(model, keep_original_model=True)

    tokenizer = AutoTokenizer.from_pretrained(tokenizer)
    pipe = pipeline('text-generation', model=model, tokenizer=tokenizer, device=config.init_device)

    with torch.autocast('cuda', dtype=DTYPE):
        result = pipe(prompt, max_new_tokens=max_output_new_tokens, do_sample=True, use_cache=True)
    
    text = result[0]["generated_text"]

    if not output:
      return text
      
    Path(output).write_text(text)

if __name__ == '__main__':
  fire.Fire(generate)