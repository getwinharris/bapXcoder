# bapX Coder - Advanced AI-Powered PWA IDE

bapX Coder is an advanced, cross-platform PWA (Progressive Web App) Integrated Development Environment featuring the "bapX Coder" AI persona. This comprehensive multimodal AI-powered development environment includes chat interface, voice input/output, image analysis (OCR), encoding-aware text processing (Base64, ASCII, Unicode, etc.), web search, Git integration with OAuth, and all necessary tools for local AI development. The project automatically downloads the Qwen3VL model for completely offline usage after setup. Works on Mac, Windows, Linux and mobile devices through any modern web browser.

## Advanced Encoding & Internationalization Support

bapX Coder includes comprehensive support for multiple text encodings and international character sets:

- **UTF-8/Unicode Support**: Full support for international characters and symbols
- **Base64 Encoding/Decoding**: For binary content and data transfer
- **Hexadecimal Support**: For hex-encoded data processing
- **ASCII Compatibility**: For legacy systems and safe text handling
- **Automatic Encoding Detection**: Detects and handles various file encodings automatically
- **International Character Sets**: Processes text in multiple languages without issues

## Why bapXcoder Exists

Traditional development tools have critical limitations:

• **Cloud IDEs** → quota walls
• **Web AIs** → session loss
• **Ollama** → model runs locally, but has no repo-wide awareness
• **IDE copilots** → partial context, token truncation, silent edits

So bapXcoder is:

• **A deterministic CLI-first dev tool** with inbuilt model without losing repo-level awareness
• **Local model (Qwen3VL)** never hits quota
• **"Local ollama models are not automatically connected to the whole repo like CLI"**
• **Local, quota-free, repo-aware AI IDE** that doesn't require extensions like VSCode
• **One session for one project** with one todo list for one project on a certain path
• **Aware of diff to Git Repo** after file updates

## bapXcoder IDE Capabilities

The bapXcoder IDE leverages the power of the Qwen3-VL model and provides a comprehensive development environment:

### Core AI Capabilities:
- **Multimodal Processing**: Advanced vision-language understanding for image analysis, OCR, document processing
- **Code Assistance**: Real-time coding help and suggestions with context awareness
- **Voice Features**: Speech-to-text for input and text-to-speech for auto-play output
- **Web Research**: Integrated search for current information and research retrieval
- **File Analysis**: Attach and analyze code, image, and document files directly

### Project-Based Features:
- **Project Memory System**: Each project gets its own `.bapXcoder` directory with persistent `todo.json` and `sessiontree.json`
- **Task Management**: Project-specific to-do lists with priority and completion tracking
- **Session Tracking**: Activity logs and context preservation per project session
- **File Organization**: Automatic project structure maintenance with AI-aware file handling

### CLI Integration:
- **Integrated Terminal**: Built-in command line interface within the web IDE
- **Project Context**: Commands execute within the current project directory
- **Git Integration**: Full Git operations with OAuth support
- **File Operations**: Direct file manipulation through CLI within IDE

### Live Syntax Checking & Validation:
- **Real-time Syntax Validation**: Checks syntax as you type without LSP overhead
- **Multi-language Support**: Python, JavaScript, TypeScript, HTML, CSS, JSON, and more
- **File Monitoring**: Automatically detects file changes and validates syntax
- **Error Reporting**: Provides line/column specific error messages
- **Deterministic Validation**: Uses language-specific parsers and compilers for accurate checking
- **No Silent Failures**: Explicit syntax feedback prevents hidden issues

### Research & Analysis:
- **Web Retrieval**: RAG (Retrieval Augmented Generation) for online research
- **Document Analysis**: Process multi-page documents, tables, and complex content
- **Code Understanding**: Deep analysis of code structure and dependencies across files
- **Visual Processing**: OCR and GUI element recognition for screenshot-to-code features

### Testing & Validation:
- **Built-in Test Suite**: Automated validation of user projects developed with the IDE
- **Code Quality Checks**: Syntax validation and error detection for multiple languages
- **Feature Utilization Tracking**: Validates proper use of IDE features in your projects
- **Run Buttons**: Each file tab has a run button for immediate execution testing

### Installation Wizard:
- **Automatic Dependency Check**: Verifies Python, required packages, system resources
- **Permission-based Installation**: Asks user permission before installing any dependencies
- **System Validation**: Checks for sufficient RAM, disk space, OS compatibility
- **Model Verification**: Confirms model file presence or initiates download

- **bapX Coder AI Persona**: Advanced AI programming assistant with specialized coding expertise
- Run Qwen3VL model locally without internet connection (after setup)
- Interactive chat interface with conversation history
- Voice input using Speech-to-Text (STT)
- Voice output with auto-play using Text-to-Speech (TTS)
- Image analysis and OCR capabilities (with file attachment)
- Integrated web search functionality
- Git OAuth integration for repository access
- Support for Git operations (clone, pull, push, etc.)
- Integrated CLI/terminal emulator for command execution
- File system access and project management
- Single prompt execution
- Configurable parameters (temperature, max tokens, etc.)
- Complete offline functionality - no cloud dependencies after setup
- Auto-download of model from Hugging Face during initial setup
- Cross-platform PWA (Progressive Web App) - works on Mac, Windows, Linux, and mobile
- Installable on any device like a native application
- Modern dark theme with purple accent color
- Rich text editor for code editing with syntax highlighting
- Integrated development tools for AI-assisted coding

## Prerequisites

1. **Python 3.8+** installed on your system
2. A system capable of running large language models (sufficient RAM, and optionally GPU)
3. Git (to clone the repository)
4. Internet connection (for initial model download during setup)
5. Sufficient disk space (~9GB for complete setup: model weights (~8.76GB) + configurations + tools)
6. Web browser (for the GUI interface)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/getwinharris/bapXcoder.git
   # OR using SSH:
   git clone git@github.com:getwinharris/bapXcoder.git
   cd bapXcoder
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: bapX Coder is a web-based PWA application that runs in your browser. No native installers (.exe, .dmg, etc.) are required. Once installed, simply run the server and access the IDE through any modern web browser.

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
- ✅ **PWA functionality works offline after initial setup**

The model file is downloaded from Hugging Face once during setup, eliminating the need for cloud APIs or ongoing compute charges during inference.

## Usage

bapX Coder runs as a web-based PWA accessible through your browser on any platform:

```bash
python qwen3VL_local_cli.py
```

Then open your browser to `http://localhost:7860`

After accessing the application in your browser, you can install it as a PWA on your device (Mac, Windows, Linux, or mobile) using your browser's install option for a native app-like experience.

### Features in the Web Interface:
- **Chat Panel**: AI-powered conversation with the Qwen3VL model
- **Terminal Panel**: Integrated CLI for running commands
- **Code Editor**: Syntax-highlighted editor for code development
- **File Explorer**: Navigate and manage project files
- **Settings Panel**: Configure model parameters and preferences

### Command Line Options

```bash
python qwen3VL_local_cli.py [options]
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
python qwen3VL_local_cli.py
```

#### Start the IDE on a custom port:
```bash
python qwen3VL_local_cli.py --port 8080
```

#### Using GPU Acceleration:
```bash
python qwen3VL_local_cli.py --gpu-layers 20
```

After starting, open your web browser to `http://localhost:7860` to access the bapX Coder interface.

## Interactive Features

### bapX Coder AI Assistant
- Advanced AI programming assistant with specialized coding expertise
- Context-aware responses based on your project
- Multi-modal capabilities (can analyze text, code, and attached images)

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
- Image analysis and OCR when files are attached

### File Management
- Browse project files
- Create, edit and delete files
- Navigate directory structure

### Web Search Integration
- Built-in web search functionality
- Get up-to-date information within the chat interface
- Search results integrated with AI responses

### Git Integration
- OAuth authentication for Git services
- Repository cloning and management
- Git operations (clone, pull, push) from the interface

### Voice Features
- Speech-to-Text (STT) for voice input
- Text-to-Speech (TTS) with auto-play for responses
- Voice command support

### File Attachment
- Attach images for OCR and analysis
- Attach code files for review and suggestions
- Support for multiple file types

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

1. **Model file not found**: The model will be downloaded automatically when first run, or you can run `python download_model.py` manually. The complete setup requires ~9GB: model weights (~8.76GB) + configurations + tools. The model will be saved as Qwen3VL-8B-Instruct-Q8_0.gguf.

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

## Acknowledgments

This project was inspired by the innovative work at continue.dev, Google's CLI tools, Google Antigravity, and similar Qwen-based coding interfaces. We appreciate their contributions to AI-assisted development tools.

## About the Qwen3VL Model

The Qwen3-VL model powering bapX Coder is the most powerful vision-language model in its generation, delivering comprehensive upgrades across the board:

- **Superior text understanding & generation**, deeper visual processing capabilities
- **Visual Agent**: Operates PC/mobile GUIs—recognizes elements, understands functionality
- **Visual Coding Boost**: Generates Draw.io/HTML/CSS/JS from images
- **Advanced Spatial Perception**: Judges object positions, viewpoints, and occlusions; provides stronger 2D grounding and enables 3D grounding
- **Long Context & Video Understanding**: Native 256K context, expandable to 1M; handles books and hours-long videos
- **Upgraded Visual Recognition**: Broader, higher-quality pretraining is able to "recognize everything"—celebrities, anime, products, landmarks, flora/fauna
- **Expanded OCR**: Supports 32 languages (up from 19); robust in low light, blur, and tilt; better with rare/ancient characters and jargon
- **Text Understanding**: Enhanced capabilities for complex document analysis

The Qwen3VL model is available as an open-source model from Alibaba Cloud. These files are compatible with llama.cpp, Ollama, and other GGUF-based tools, supporting inference on CPU, NVIDIA GPU (CUDA), Apple Silicon (Metal), Intel GPUs (SYCL), and more. You can mix precisions for optimal performance.

Thank you to Alibaba for making this powerful multimodal model available as open source, enabling projects like bapX Coder to provide advanced AI capabilities locally without cloud dependencies.

## bapX Coder IDE Capabilities Powered by Qwen3-VL & Project-Based Architecture

Our IDE leverages the powerful Qwen3-VL model combined with our architectural innovations to provide unique capabilities:

### Advanced Multimodal AI Assistance
- **Enhanced Vision Processing**: Using Qwen3-VL's advanced visual capabilities to analyze UI mockups, diagrams, charts, and screenshots for code generation
- **OCR Excellence**: Leveraging 32 language support and robust text extraction to process images of documents, handwritten notes, and code snippets
- **Spatial Understanding**: The AI can comprehend layouts, positioning, and visual relationships in your design materials

### Project-Based Memory System
- **Persistent Context**: Unlike cloud IDEs that lose session context, bapX Coder maintains project-specific memory with `.bapXcoder` directories
- **File-Level Association**: Todos, session trees, and conversation history are tied to individual projects, maintaining focused context
- **Cross-File Understanding**: The AI remembers relationships between files in your project, providing better contextual suggestions
- **Long-Term Learning**: The system improves its understanding of your codebase over time within each project

### CLI-Integrated Development
- **Terminal Integration**: Direct command execution within the project context for Git, build tools, and testing
- **Repo-Wide Awareness**: The AI understands the entire project structure and can suggest commands based on context
- **File System Navigation**: Direct integration with the project file structure for seamless development workflows

### Advanced Task Management
- **Project-Specific Todos**: Tasks are stored per project in `todo.json`, maintaining focus on current objectives
- **Contextual Suggestions**: AI provides task suggestions based on actual code and project structure
- **Progress Tracking**: Session trees track file usage and activity for better project management

### Web Research & Retrieval Augmentation
- **Integrated Research**: Web search capabilities within the IDE for up-to-date information retrieval
- **Contextual Results**: Search results are processed by the local AI to provide relevant, project-specific responses
- **Research Continuation**: The "Continue Reasoning" feature allows extended research sessions beyond context windows
- **Local Processing**: All retrieved information is processed locally, maintaining privacy and security

### Offline-Capable, Quota-Free Operation
- **No Usage Limits**: Unlike cloud services with token quotas, bapX Coder runs entirely locally using your hardware resources
- **Complete Privacy**: All code, conversations, and project data remain on your machine
- **Always Available**: No internet connection required after initial setup; works regardless of service availability
- **Cost-Effective**: No recurring costs once the system is set up

## Contributions Welcome

This is an open-source project and contributions are welcome! Anyone can contribute to bapX Coder development. If you find this project useful, consider contributing:

- Code improvements and bug fixes
- Feature enhancements
- Documentation updates
- Model optimization suggestions
- Community support

Feel free to fork the repository, make changes, and submit pull requests. Together we can make bapX Coder even better!

## Developed By

**Harris** ([getwinharris](https://github.com/getwinharris))
Founder, Bapx Media Hub
Coimbatore, Tamil Nadu, India

### Connect With Me
- 📘 [Facebook](https://www.facebook.com/getwinharris/)
- 🐦 [Twitter/X](https://twitter.com/getwinharris)
- 💼 [LinkedIn](https://www.linkedin.com/in/getwinharris/)
- 🐙 [GitHub](https://github.com/getwinharris)
- 📷 [Instagram](https://www.instagram.com/getwinharris/)

### Follow Bapx Media Hub
- 📺 [YouTube](https://www.youtube.com/@bapxmediahub)
- 📷 [Instagram](https://www.instagram.com/bapxmediahub/)
- 📘 [Facebook](https://www.facebook.com/bapxmediahub/)

## Testing

The bapX Coder project includes comprehensive testing tools:

- **Agent Tests**: Automated tests in `tests/test_agent.py` that validate core IDE functionality
- **User Tests**: Simulated user interactions in `tests/user_test.py` that verify user experience workflows
- **Integration Tests**: Coming soon to validate the complete AI-assisted development workflow

To run tests:
```bash
cd tests/
python test_agent.py
python user_test.py
```

## Standalone Installation with Automatic Setup

The bapX Coder installation wizard will guide you through a complete setup process:

1. **Environment Check**: Validates Python, dependencies, and system requirements
2. **Model Download**: Automatically downloads the 8.76GB Qwen3VL model once
3. **Configuration**: Sets up the project-based memory system with `.bapXcoder` directories
4. **Verification**: Tests the complete AI pipeline before first use

The installation only downloads the Qwen3-VL-8B-Instruct-Q8_0.gguf model (8.76GB) and no additional models beyond this.

## Development Tools Comparison

bapX Coder stands apart from other development environments:

| Feature | bapX Coder | Continue.dev | Antigravity IDE |
|---------|-------------|----------------|------------------|
| **Operation** | Fully offline after setup | Hybrid (local LLMs) | Cloud-based |
| **Cost** | Free forever | Subscription | Pay-per-use |
| **Privacy** | All data stays local | Local processing | Data goes to cloud |
| **Model** | Single 8.76GB Qwen3-VL model | Multiple configurable models | Various cloud models |
| **AI Capability** | Vision, OCR, text, code | Text completion | Text completion |
| **Connectivity** | Works completely offline | Needs cloud API keys | Requires internet |
| **Customization** | Project-based memory system | VS Code extensions | Browser-based |

## Capabilities via Qwen3-VL Model

The Qwen3-VL model enables these unique capabilities in bapX Coder:

- **Multimodal Understanding**: Process both text and images in the same context
- **Advanced OCR**: Recognize text from images in 32+ languages
- **Visual GUI Analysis**: Understand and interpret UI designs from screenshots
- **Code Generation from Visuals**: Create code based on UI screenshots or Draw.io diagrams
- **Document Understanding**: Process complex documents with embedded images
- **Spatial Reasoning**: Understand positional relationships in images

## Advanced CLI Integration

The integrated command line interface provides:

- **Project Context Awareness**: Commands execute within project-specific contexts
- **AI-Enhanced Commands**: Use AI to formulate appropriate CLI commands
- **File Operation Integration**: Direct file operations from the chat interface
- **Git Integration**: Full Git operations with AI-powered commit messages
- **System Integration**: Seamless integration with platform-specific tools

## Project-Based Memory System

Each project gets its own `.bapXcoder` directory with:

- `todo.json`: Project-specific task management
- `sessiontree.json`: Activity tracking and session management
- Automatic organization of project-specific context

## Web Research Integration

- **Integrated Search**: Built-in web search within the IDE
- **AI-Synthesized Results**: AI processes and summarizes search results
- **Context-Aware Research**: Research stays within project context
- **Source Attribution**: Automatic citation of information sources

## Voice and Accessibility Features

- **Speech-to-Text**: Voice input for hands-free coding
- **Text-to-Speech**: Auto-playing responses for accessibility
- **Voice Commands**: Natural language interface to IDE features

## Encoding Support

Full support for:
- UTF-8, ASCII, Base64, Hex, and other encodings
- International character sets
- Automatic encoding detection
- Binary file handling with proper encoding

## Disclaimer

This tool is for educational and personal use. Be mindful of the computational resources required to run large language models. Respect the original model's licensing terms.

## Qwen3-VL Model Capabilities

The Qwen3-VL model powering bapX Coder has extensive multimodal capabilities:

- **Visual Agent**: Can operate PC/mobile GUIs by recognizing elements and understanding functionality
- **Visual Coding Boost**: Generates Draw.io/HTML/CSS/JS from images
- **Advanced Spatial Perception**: Judges object positions, viewpoints, and occlusions
- **Long Context & Video Understanding**: Native 256K context, expandable to 1M
- **Expanded OCR**: Supports 32+ languages with robust performance in difficult conditions
- **Text Understanding**: Advanced document analysis and comprehension

## Contributions Welcome

This project welcomes contributors! If you'd like to help enhance bapX Coder:

- Report bugs or suggest features
- Contribute code improvements
- Help with documentation
- Share your use cases and feedback
- Improve multimodal processing capabilities

Join our community to make bapX Coder even better!
