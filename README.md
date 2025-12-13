# bapXcoder

A comprehensive AI-powered standalone IDE with integrated CLI, chat interface, code editor, and development tools. This project provides a complete development environment with Qwen3VL model assistance, voice features, and internal terminal access.

## Features

- Run Qwen3VL model locally without internet connection (after setup)
- Interactive chat interface with conversation history
- Voice input using Speech-to-Text (STT)
- Voice output with auto-play using Text-to-Speech (TTS)
- Integrated CLI/terminal emulator for command execution
- File system access and project management
- Single prompt execution
- Configurable parameters (temperature, max tokens, etc.)
- Complete offline functionality - no cloud dependencies after setup
- Auto-download of model from Hugging Face during initial setup
- Rich text editor for code editing with syntax highlighting
- Integrated development tools for AI-assisted coding

## Prerequisites

1. **Python 3.8+** installed on your system
2. A system capable of running large language models (sufficient RAM, and optionally GPU)
3. Git (to clone the repository)
4. Internet connection (for initial model download during setup)
5. Sufficient disk space (~8.76GB for complete setup: model weights + configurations + tools)
6. Web browser (for the GUI interface)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/getwinharris/qwen3VL-Local-IDE.git
   # OR using SSH:
   git clone git@github.com:getwinharris/qwen3VL-Local-IDE.git
   cd qwen3VL-Local-IDE
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
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

3. Download the Qwen3VL model (this will download about 5-6GB):
   ```bash
   python download_model.py
   ```
   OR you can run the IDE directly and it will prompt to download if the model is missing:
   ```bash
   python qwen3VL_local_ide.py
   ```

4. Install this package in development mode:
   ```bash
   pip install -e .
   ```

## No Cloud Charges - Automatic Model Download

Unlike cloud-based AI services, this project automatically downloads the Qwen3VL model from Hugging Face during setup. This means:

- ✅ **No subscription fees**
- ✅ **No per-token charges**
- ✅ **No internet connection required during inference** (after setup)
- ✅ **Complete privacy - all processing happens locally** (after setup)
- ✅ **One-time download during installation, unlimited local usage**

The model file is downloaded from Hugging Face once during setup, eliminating the need for cloud APIs or ongoing compute charges during inference.

## Usage

The IDE runs as a web application accessible through your browser:

```bash
python qwen3VL_local_ide.py
```

Then open your browser to `http://localhost:7860`

### Features in the Web Interface:
- **Chat Panel**: AI-powered conversation with the Qwen3VL model
- **Terminal Panel**: Integrated CLI for running commands
- **Code Editor**: Syntax-highlighted editor for code development
- **File Explorer**: Navigate and manage project files
- **Settings Panel**: Configure model parameters and preferences

### Command Line Options

```bash
python qwen3VL_local_ide.py [options]
```

- `--model PATH`: Path to the GGUF model file (default: Qwen3VL-8B-Instruct-Q8_0.gguf)
- `--port PORT`: Port to run the web interface (default: 7860)
- `--host HOST`: Host address (default: 127.0.0.1)
- `--max-tokens N`: Maximum tokens to generate (default: 512)
- `--temperature T`: Sampling temperature (default: 0.7)
- `--threads N`: Number of CPU threads (default: 4)
- `--context-size N`: Context size in tokens (default: 4096)
- `--gpu-layers N`: Number of GPU layers (0 for CPU only, default: 0)
- `--help`: Show this help message

### Examples

#### Start the IDE:
```bash
python qwen3VL_local_ide.py
```

#### Start the IDE on a custom port:
```bash
python qwen3VL_local_ide.py --port 8080
```

#### Using GPU Acceleration:
```bash
python qwen3VL_local_ide.py --gpu-layers 20
```

## Interactive Features

### Code Editing
- Syntax-highlighted editor
- Real-time AI suggestions
- Code completion assistance

### Integrated Terminal
- Execute shell commands directly in the IDE
- Path context aware (runs in current project directory)
- Output displayed in the terminal panel

### AI-Powered Assistance
- Ask questions about your project
- Get code suggestions
- Explain code functionality
- Debug assistance

### File Management
- Browse project files
- Create, edit and delete files
- Navigate directory structure

## Configuration File

The project includes a `config.ini` file that allows you to set default values for:
- Model path
- Max tokens
- Temperature
- CPU threads
- Context size
- GPU layers
- Web server settings

## Performance Tips

1. **CPU Threading**: Adjust the number of threads based on your CPU cores for optimal performance.

2. **GPU Acceleration**: Use GPU layers to speed up inference if you have compatible hardware.

3. **Context Size**: Reduce the context size if you're experiencing memory issues.

4. **Memory Requirements**: Qwen3VL in Q8_0 format is relatively memory efficient, but you'll need at least 8GB RAM for the 8B model.

## Troubleshooting

### Common Issues

1. **Model file not found**: The model will be downloaded automatically when first run, or you can run `python download_model.py` manually. The complete setup requires ~8.76GB: model weights (~5-6GB) + configurations + tools. The model will be saved as Qwen3VL-8B-Instruct-Q8_0.gguf.

2. **Dependencies not found**: Install all dependencies using `pip install -r requirements.txt`.

3. **Memory errors**: Reduce the context size or close other applications to free up RAM. The model requires at least 8GB RAM to run efficiently.

4. **Slow responses**: Consider using GPU acceleration if you have a compatible GPU.

5. **Download fails**: Check your internet connection. The model file is downloaded from Hugging Face directly.

6. **Voice features not working**: Ensure your system has working microphone and speakers. On some systems you may need to grant permissions for microphone access.

7. **Web interface not loading**: Check that the port is not being used by another application and that your firewall allows the connection.

### Installation Issues

If you're having trouble installing `llama-cpp-python`, try:

```bash
# Force reinstall
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python
```

## Comparison to Continue.dev and JetBrains

This project differs from cloud-based development tools in several key ways:

| Aspect | [bapXcoder](https://github.com/getwinharris/bapXcoder) | [Continue.dev](https://continue.dev) | JetBrains IDEs |
|--------|------------------|------------------|------------------|
| **Deployment** | Completely local web-based IDE | Mixed (CLI tool with local LLMs) | Desktop applications with some cloud features |
| **Costs** | Free after initial setup | Free with optional paid features | Paid licenses |
| **Privacy** | All data stays local | Local processing with local LLMs | Data stays local mostly |
| **Connectivity** | Works offline after setup | Requires internet for setup | Works offline mostly |
| **Model Access** | Auto-download from Hugging Face during setup | Configurable LLMs | N/A |
| **Customization** | Full local control | High customization | High customization |
| **Integrated CLI** | Built-in terminal in web interface | VS Code integrated terminal | Built-in terminal |
| **AI Integration** | Full AI assistant with chat & code generation | AI-powered commands and context | Plugin-based AI features |

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use. Be mindful of the computational resources required to run large language models. Respect the original model's licensing terms.
