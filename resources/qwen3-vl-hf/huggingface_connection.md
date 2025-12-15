# Connecting to Hugging Face Qwen3-VL Model without Downloading

## Overview
This document explains how to connect to the Hugging Face Qwen3-VL model using llama-cpp-python without manually downloading the model file first.

## Requirements
- Python 3.8+
- `llama-cpp-python` package
- `huggingface-hub` package
- Internet connection for first-time access

## Installation
```bash
pip install llama-cpp-python
pip install huggingface-hub
```

## Method 1: Direct Connection with from_pretrained

### Basic Usage
```python
from llama_cpp import Llama

# Connect directly to the Qwen3-VL model on Hugging Face
llm = Llama.from_pretrained(
    repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
    filename="*Q8_0.gguf",  # Wildcard to match Q8_0 quantized version
    verbose=False
)

# Use the model for text generation
response = llm(
    "Hello, how are you?",
    max_tokens=128,
    stop=["Q:", "\n"],
    echo=True
)

print(response)
```

### For Vision-Language Models (like Qwen3-VL)
For vision-language models, the connection includes both the main model and the vision encoder (mmproj):

```python
from llama_cpp import LlamaVision

# Connect to the vision-language model
llm_vision = LlamaVision.from_pretrained(
    repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
    filename="*Q8_0.gguf",  # Main model file
    verbose=False
)

# For image processing, you also need the vision encoder
# This can be loaded similarly from the same repository
```

### Advanced Configuration
```python
from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
    filename="*Q8_0.gguf",
    n_ctx=4096,  # Context size
    n_threads=8,  # Number of threads to use
    n_gpu_layers=-1,  # Use all layers on GPU (if available)
    verbose=False
)
```

## Method 2: Using OpenAI-Compatible Server

### Start the Server
```bash
python3 -m llama_cpp.server \
  --hf_model_repo_id Qwen/Qwen3-VL-8B-Instruct-GGUF \
  --model '*Q8_0.gguf' \
  --n_ctx 4096 \
  --n_threads 8
```

### Connect to the Server
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-no-key-required",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ],
    temperature=0.7,
    max_tokens=128
)

print(response.choices[0].message.content)
```

## Method 3: Using Hugging Face Hub Direct Access

```python
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# This downloads to the cache but you don't specify a location
model_path = hf_hub_download(
    repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
    filename="Qwen3VL-8B-Instruct-Q8_0.gguf",
    local_files_only=False  # Allow downloading if not in cache
)

# Load the model from cache location
llm = Llama(
    model_path=model_path,
    n_ctx=4096,
    verbose=False
)
```

## Integration with bapXcoder

To integrate this with your bapXcoder project, you could modify your model initialization code:

```python
def initialize_qwen3_vl_model():
    """Initialize Qwen3-VL model directly from Hugging Face Hub"""
    try:
        from llama_cpp import Llama
        from huggingface_hub import hf_hub_download
        
        # Option 1: Direct from_pretrained (recommended)
        model = Llama.from_pretrained(
            repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
            filename="*Q8_0.gguf",
            n_ctx=4096,
            n_threads=os.cpu_count() // 2,  # Use half of available threads
            n_gpu_layers=-1 if torch.cuda.is_available() else 0,
            verbose=False
        )
        
        return model
    except ImportError:
        print("Please install: pip install llama-cpp-python huggingface-hub")
        return None
    except Exception as e:
        print(f"Error initializing model: {e}")
        return None
```

## Cache Management

Since the model is cached after first use, you can manage it:

### Check cache size
```bash
huggingface-cli scan-cache
```

### Delete specific models from cache
```bash
huggingface-cli delete-cache --repos Qwen/Qwen3-VL-8B-Instruct-GGUF
```

### Set custom cache directory
```python
import os
os.environ['HF_HOME'] = '/path/to/custom/cache'
```

## Performance Considerations

1. **First-time access**: Will take longer as model downloads to cache
2. **Subsequent access**: Will be faster using cached model
3. **Memory usage**: Model will use system memory/GPU memory as configured
4. **Quantization**: Using Q8_0 or other quantized versions reduces memory usage

## Error Handling

```python
def safe_model_load():
    try:
        from llama_cpp import Llama
        model = Llama.from_pretrained(
            repo_id="Qwen/Qwen3-VL-8B-Instruct-GGUF",
            filename="*Q8_0.gguf",
            verbose=False
        )
        return model
    except Exception as e:
        print(f"Could not load model from Hugging Face: {e}")
        print("Falling back to local model file...")
        # Fall back to your existing local model loading
        return None
```

## Advantages Over Manual Download

1. **Automatic management**: Model is automatically cached and managed
2. **No manual file handling**: No need to manually download and place files
3. **Version control**: Easy to switch between different model versions
4. **Space efficiency**: Models are shared across different projects
5. **Automatic updates**: Can easily update to newer model versions
6. **Fallback support**: Can implement fallback to local files if needed

## Disadvantages vs Local Download

1. **Internet dependency**: First-time access requires internet
2. **Initial latency**: First use will have download time
3. **Cache storage**: Uses local storage for caching (like manual download)
4. **Version stability**: Could have issues if model files change on HF

This approach allows you to connect to Hugging Face models without manually downloading them first, while still maintaining offline capabilities after the first load.