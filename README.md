# bapXcoder

A command-line interface tool for running the Qwen3VL model locally using llama.cpp. This project includes the model file directly in the repository for completely offline usage.

## Features

- Run Qwen3VL model locally without internet connection
- Interactive chat mode
- Single prompt execution
- Configurable parameters (temperature, max tokens, etc.)
- Complete offline functionality - no cloud dependencies
- Included model file in repository - no separate downloads needed

## Prerequisites

1. **Python 3.8+** installed on your system
2. A system capable of running large language models (sufficient RAM, and optionally GPU)
3. Git (to clone the repository)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/getwinharris/qwen3VL-Local-CLI.git
   # OR using SSH:
   git clone git@github.com:getwinharris/qwen3VL-Local-CLI.git
   cd qwen3VL-Local-CLI
   ```

2. Install the required dependencies:
   ```bash
   pip install llama-cpp-python
   ```

   For GPU acceleration:
   - **NVIDIA GPU (CUDA)**:
     ```bash
     CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
     ```
   - **Apple Silicon (Metal)**:
     ```bash
     CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
     ```
   - **AMD GPU (ROCm)**:
     ```bash
     CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python
     ```

3. Install this package in development mode:
   ```bash
   pip install -e .
   ```

## No Cloud Charges or Model Downloads Required

Unlike cloud-based AI services, this project includes the Qwen3VL model directly in the repository. This means:

- ✅ **No subscription fees**
- ✅ **No per-token charges**
- ✅ **No internet connection required during inference**
- ✅ **Complete privacy - all processing happens locally**
- ✅ **One-time download, unlimited local usage**

The model file is provided as part of this repository, eliminating the need for cloud APIs, model downloading from external sources, or ongoing compute charges.

## Usage

### Command Line Options

```bash
python qwen3VL_local_cli.py [options]
```

- `--model PATH`: Path to the GGUF model file (default: looks for model in current directory)
- `--prompt TEXT`: Direct prompt to send to the model
- `--interactive, -i`: Start interactive chat mode
- `--max-tokens N`: Maximum tokens to generate (default: 512)
- `--temperature T`: Sampling temperature (default: 0.7)
- `--threads N`: Number of CPU threads to use (default: 4)
- `--context-size N`: Context size in tokens (default: 4096)
- `--gpu-layers N`: Number of GPU layers (0 for CPU only, default: 0)
- `--help-model`: Show detailed configuration help

### Examples

#### Single Prompt
```bash
python qwen3VL_local_cli.py --prompt "Explain how photosynthesis works"
```

#### Interactive Chat Mode
```bash
python qwen3VL_local_cli.py -i
```

#### With Custom Parameters
```bash
python qwen3VL_local_cli.py --prompt "Write a short story" --temperature 0.9 --max-tokens 1024
```

#### Using GPU Acceleration
```bash
python qwen3VL_local_cli.py --prompt "Hello!" --gpu-layers 20
```

## Interactive Mode Commands

While in interactive mode, you can use these special commands:

- `help` - Show available commands
- `reset` - Reset conversation history
- `clear` - Clear the screen
- `quit`, `exit`, or `q` - Exit the program

## Configuration File

The project includes a `config.ini` file that allows you to set default values for:
- Model path
- Max tokens
- Temperature
- CPU threads
- Context size
- GPU layers

## Performance Tips

1. **CPU Threading**: Adjust the number of threads based on your CPU cores for optimal performance.

2. **GPU Acceleration**: Use GPU layers to speed up inference if you have compatible hardware.

3. **Context Size**: Reduce the context size if you're experiencing memory issues.

4. **Memory Requirements**: Qwen3VL in Q8_0 format is relatively memory efficient, but you'll need at least 8GB RAM for the 8B model.

## Troubleshooting

### Common Issues

1. **Model file not found**: The model file should be included in the repository in the same directory.

2. **llama-cpp-python not found**: Install it using the instructions above.

3. **Memory errors**: Reduce the context size or close other applications to free up RAM.

4. **Slow responses**: Consider using GPU acceleration if you have a compatible GPU.

### Installation Issues

If you're having trouble installing `llama-cpp-python`, try:

```bash
# Force reinstall
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
```

## Comparison to QwenLM/qwen-code

This project differs from the cloud-based QwenLM/qwen-code repository in several key ways:

| Aspect | [qwen3VL-Local-CLI](https://github.com/getwinharris/qwen3VL-Local-CLI) | [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) |
|--------|------------------|------------------|
| **Deployment** | Completely local | Cloud-based API |
| **Costs** | Free after initial setup | Ongoing usage costs |
| **Privacy** | All data stays local | Data sent to cloud |
| **Connectivity** | Works offline | Requires internet |
| **Model Access** | Included in repo | API-based access |
| **Customization** | Full local control | Limited by API |

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use. Be mindful of the computational resources required to run large language models. Respect the original model's licensing terms.
