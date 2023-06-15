from llama_cpp import Llama

llm = Llama(model_path="./llama/hf/pytorch_model-00001-of-00002.bin")

output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)

print(output)