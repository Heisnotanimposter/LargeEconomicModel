#!pip install -q -U immutabledict sentencepiece 
#!git clone https://github.com/google/gemma_pytorch.git

import contextlib
import torch
import os
#import kagglehub

import sys 
sys.path.append("/Users/seungwonlee/LargeEconomicModel/Future Strategy Maker/gemma_pytorch/") 

from gemma.config import get_model_config
from gemma.model import GemmaForCausalLM

# Choose variant and machine type
VARIANT = '1b'
MACHINE_TYPE = 'cpu'
OUTPUT_LEN = 200
METHOD = 'it'

#weights_dir = kagglehub.model_download(f"google/gemma-3/pytorch/gemma-3-{VARIANT}-{METHOD}/1")
#/Users/seungwonlee/LargeEconomicModel/gemma-3-pytorch-gemma-3-1b-it-v1
weights_dir = kagglehub.model_download(f"/Users/seungwonlee/LargeEconomicModel/gemma-3-pytorch-gemma-3-1b-it-v1")

tokenizer_path = os.path.join(weights_dir, 'tokenizer.model')
ckpt_path = os.path.join(weights_dir, f'model.ckpt')

# Set up model config.
model_config = get_model_config(VARIANT)
model_config.dtype = "float32" if MACHINE_TYPE == "cpu" else "float16"
model_config.tokenizer = tokenizer_path

@contextlib.contextmanager
def _set_default_tensor_type(dtype: torch.dtype):
    """Sets the default torch dtype to the given dtype."""
    torch.set_default_dtype(dtype)
    yield
    torch.set_default_dtype(torch.float)

# Instantiate the model and load the weights.
device = torch.device(MACHINE_TYPE)
with _set_default_tensor_type(model_config.get_dtype()):
    model = GemmaForCausalLM(model_config)
    model.load_weights(ckpt_path)
    model = model.to(device).eval()

# Generate
USER_CHAT_TEMPLATE = "<start_of_turn>user\n{prompt}<end_of_turn>\n"
MODEL_CHAT_TEMPLATE = "<start_of_turn>model\n{prompt}<end_of_turn>\n"

model.generate(
    USER_CHAT_TEMPLATE.format(prompt="What is a good place for travel in the US?") +
    MODEL_CHAT_TEMPLATE.format(prompt="California.") + 
    USER_CHAT_TEMPLATE.format(prompt="What can I do in California?") +
    "<start_of_turn>model\n", 
    device, 
    output_len=OUTPUT_LEN
)

