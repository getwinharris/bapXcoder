# bapXcoder - Advanced AI-Powered PWA IDE

bapXcoder is an advanced, cross-platform PWA (Progressive Web App) Integrated Development Environment featuring the "bapXcoder" AI persona. This comprehensive multimodal AI-powered development environment includes chat interface, voice input/output, image analysis (OCR), encoding-aware text processing (Base64, ASCII, Unicode, etc.), web search, Git integration with OAuth, and all necessary tools for AI development. The project uses a dual-model architecture with Interpreter model (bapXcoder-VL) handling user communication and context management, and Developer model (bapXcoder-Coder) for specialized coding tasks, connecting via llama.cpp to models. Works on Mac, Windows, Linux and mobile devices through any modern web browser. 

## Key Architecture: Dual-Model Pipeline

The bapXcoder project implements a sophisticated dual-model architecture:

### Interpreter Model (bapXcoder-VL)
- **Handles**: All user communication, multimodal processing, OCR, voice input/output, web research
- **Responsibility**: Maintains session context, processes user input, manages project state
- **Connection**: Via llama.cpp runtime to Hugging Face models

### Developer Model (bapXcoder-Coder)
- **Handles**: All coding tasks, code generation, analysis, implementation based on structured instructions
- **Responsibility**: Executes only structured instructions received from Interpreter model
- **Connection**: Via llama.cpp runtime to Hugging Face models

**Important**: All user prompts go to the Interpreter; the Developer never communicates directly with the user - it only executes structured instructions from the Interpreter.

## Installation

### Prerequisites
1. **Python 3.8+** installed on your system
2. **Git** (to clone the repository)
3. **Sufficient disk space** (for dependencies and runtime)
4. **Web browser** (for the GUI interface)
5. **Internet connection** (for model access via llama.cpp runtime)
6. **RAM**: At least 8GB recommended for optimal performance

### Method 1: Single Executable Installation (Recommended)
1. Visit our main page at [https://getwinharris.github.io/bapXcoder/](https://getwinharris.github.io/bapXcoder/)
2. Follow the download instructions to get the single executable file
3. Run the installer which handles everything automatically:
   - Clones the repository
   - Installs dependencies
   - Configures llama.cpp runtime connection
   - Sets up project memory system

### Method 2: Manual Installation
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

## Usage

bapXcoder runs as a web-based PWA accessible through your browser on any platform:

```bash
python bapxcoder_local_cli.py
```

Then open your browser to `http://localhost:7860`

After accessing the application in your browser, you can install it as a PWA on your device (Mac, Windows, Linux, or mobile) using your browser's install option for a native app-like experience.

## Core AI Capabilities:

### Interpreter Model (bapXcoder-VL)
- **Multimodal Processing**: Advanced vision-language understanding for image analysis, OCR, document processing
- **Voice Features**: Speech-to-text for input and text-to-speech for auto-play output
- **Web Research**: Integrated search for current information and research retrieval
- **File Analysis**: Attach and analyze images and documents directly

### Developer Model (bapXcoder-Coder)
- **Code Assistance**: Real-time coding help and suggestions with context awareness based on structured instructions from Interpreter
- **File Analysis**: Attach and analyze code files directly

### Dual-Model Pipeline
- **Structured Instructions**: All user prompts go to Interpreter which converts them to structured instructions for Developer
- **Mediated Communication**: Interpreter manages all user interactions while coordinating specialized coding tasks to Developer
- **Context Management**: Interpreter maintains session context and project state

## Advanced Encoding & Internationalization Support

bapXcoder includes comprehensive support for multiple text encodings and international character sets:
- **UTF-8/Unicode Support**: Full support for international characters and symbols
- **Base64 Encoding/Decoding**: For binary content and data transfer
- **Hexadecimal Support**: For hex-encoded data processing
- **ASCII Compatibility**: For legacy systems and safe text handling
- **Automatic Encoding Detection**: Detects and handles various file encodings automatically
- **International Character Sets**: Processes text in multiple languages without issues

## CLI-First Architecture with Web UI Overlay

bapXcoder implements a sophisticated dual-server model:
- **Frontend Server** (hosted on Hostinger): Handles authentication, payments, and landing page
- **Local Application** (downloaded by users): Full IDE functionality with llama.cpp runtime model connections

**Backend Architecture:**
- **Authentication Server**: Flask/SocketIO server handling GitHub/Google OAuth and Stripe payments
- **User Data Storage**: Encrypted subscription metadata stored in GitHub repositories (not our servers)
- **Model Handlers**: Dual-model architecture - Interpreter model (bapXcoder-VL) for communication/UI and Developer model (bapXcoder-Coder) for coding tasks, both accessing models via llama.cpp runtime, no local storage required
- **Project Manager**: Project_explorer.py handles local file operations via CLI
- **Validation System**: AI-driven testing (validation_system.py) runs entirely locally
- **Project Memory**: .bapXcoder directories with persistent todo.json and sessiontree.json stored locally
- **Dual-Model Coordinator**: Interpreter model (bapXcoder-VL) acts as coordinator, receiving all user prompts and issuing structured instructions to Developer model (bapXcoder-Coder)

## Project-Based Memory System
- **Persistent Context**: Unlike cloud IDEs that lose session context, bapXcoder maintains project-specific memory with `.bapXcoder` directories
- **File-Level Association**: Todos, session trees, and conversation history are tied to individual projects, maintaining focused context
- **Local Session Memory**: Only session + RAG context lives locally in `.bapXcoder` directories
- **Cross-File Understanding**: The AI remembers relationships between files in your project, providing better contextual suggestions
- **Long-Term Learning**: The system improves its understanding of your codebase over time within each project

## Resources Integration
The project includes a `resources/` directory with reference implementations and documentation:
- **bapXcoder Code Resources**: `resources/qwen-code/` - Reference for CLI workflow patterns and direct model connection approaches
- **bapXcoder Developer Resources**: `resources/developer_agent/` - Reference for advanced coding model capabilities (archived reference)
- **Codespaces Resources**: `resources/codespaces-base/` - Reference for development environment concepts
- **Hugging Face Connection Documentation**: `resources/qwen3-vl-hf/` - Documentation on direct model access approaches (archived reference)

These resources provide insight into implementation patterns but are not part of the main application distribution.

## Web Interface Integration
- **Landing Page**: Marketing and authentication interface hosted on Hostinger
- **GitHub Integration**: Secure OAuth authentication with encrypted data storage
- **Payment Processing**: Stripe integration for subscription management
- **Download Management**: Authorized downloads only after subscription validation

## Web Research & Retrieval Augmentation
- **Integrated Research**: Web search capabilities within the IDE for up-to-date information retrieval
- **Contextual Results**: Search results are processed by the Interpreter model to provide relevant, project-specific responses via runtime connections
- **Research Continuation**: The "Continue Reasoning" feature allows extended research sessions beyond context windows
- **Secure Processing**: All retrieved information is processed with privacy and security maintained

## Advanced CLI Integration
- **Integrated Terminal**: Built-in command line interface within the web IDE
- **Direct System Integration**: All functionality executed via CLI commands underneath the web UI
- **Project Context**: Commands execute within the current project directory
- **Git Integration**: Full Git operations with OAuth support via CLI
- **File Operations**: Direct file manipulation through CLI operations, with web UI providing convenience layer
- **System Integration**: All system interactions handled via terminal commands at the backend

## Voice Features
- **Speech-to-Text (STT)**: Voice input for hands-free coding
- **Text-to-Speech (TTS)**: Auto-playing responses for accessibility
- **Auto-play Functionality**: Responses automatically played through TTS
- **Voice Commands**: Natural language interface to IDE features

## Project-Based Features:
- **Project Memory System**: Each project gets its own `.bapXcoder` directory with persistent `todo.json` and `sessiontree.json`
- **Task Management**: Project-specific to-do lists with priority and completion tracking
- **Session Tracking**: Activity logs and context preservation per project session
- **File Organization**: Automatic project structure maintenance with AI-aware file handling

## Phase-Based Auto Execution & Testing
- **AI-Driven Testing System**: Interpreter model (bapXcoder-VL) coordinates comprehensive validation that validates code after each change
- **Individual File Testing**: Each file tab has its own "Test & Validate File" button (play icon)
- **Project-Wide Validation**: "Validate Full Project" button for complete project analysis
- **Phase-Based Execution**: System tracks validation history and project phases through sessiontree.json
- **Run Primary Project File**: Left sidebar menu includes run buttons for executing primary project files
- **AI-Integrated Testing**: Interpreter model mediates interactions with AI to execute tests from the test folder

## Dual-Model Connection & Installation Process
- **Runtime-Based Access**: Both bapXcoder-VL (Interpreter) and bapXcoder-Coder (Developer) models accessed via llama.cpp runtime without local storage
- **No Local Storage Required**: Models accessed via llama.cpp runtime with runtime access
- **Runtime Integration**: Direct connection to bapXcoder models using llama-cpp-python
- **Dual-Model Pipeline**: Interpreter model (bapXcoder-VL) manages all user interaction; Developer model (bapXcoder-Coder) executes structured instructions only
- **Quota-Free Access**: Runtime-based access without storage quotas

## Advanced Multimodal AI Assistance
- **Dual-Model Processing**: Interpreter model (bapXcoder-VL) handles communication, UI understanding, and multimodal tasks while Developer model (bapXcoder-Coder) specializes in coding activities
- **Enhanced Vision Processing**: Using Interpreter model's (bapXcoder-VL) advanced visual capabilities to analyze UI mockups, diagrams, charts, and screenshots - then coordinating with Developer model (bapXcoder-Coder) for code generation
- **OCR Excellence**: Leveraging Interpreter model's (bapXcoder-VL) 32 language support and robust text extraction to process images of documents, handwritten notes, and code snippets
- **Spatial Understanding**: Interpreter model (bapXcoder-VL) comprehends layouts, positioning, and visual relationships in design materials, then coordinates with Developer model (bapXcoder-Coder) for implementation
- **Specialized Code Generation**: Developer model (bapXcoder-Coder) focuses on high-quality code generation based on Interpreter model's (bapXcoder-VL) understanding and user requirements

## Capabilities via Dual-Model Architecture

The dual-model architecture with bapXcoder-VL and bapXcoder-Coder via llama.cpp runtime enables these unique capabilities in bapXcoder:

- **Full repo context**: Interpreter model (bapXcoder-VL) processes entire project context for comprehensive understanding
- **Persistent memory**: Session-based memory system keeps context across runs
- **Multimodal Understanding**: Interpreter model (bapXcoder-VL) processes both text and images in the same context
- **Advanced OCR**: Interpreter model (bapXcoder-VL) recognizes text from images in 32+ languages
- **Visual GUI Analysis**: Interpreter model (bapXcoder-VL) understands and interprets UI designs from screenshots
- **Instruction Translation**: Interpreter model converts user intent into structured instructions for Developer model
- **Document Understanding**: Interpreter model (bapXcoder-VL) processes complex documents with embedded images
- **Spatial Reasoning**: Interpreter model (bapXcoder-VL) understands positional relationships in images
- **Specialized Coding**: Developer model (bapXcoder-Coder) handles all coding tasks with advanced code understanding and generation
- **Dual-Model Pipeline**: All user prompts go to Interpreter; Developer executes only structured instructions from Interpreter
- **Mediated Communication**: Interpreter manages all user interactions while Developer focuses on structured task execution
- **Deterministic Behavior**: Predictable session-based intelligence that persists between runs

## Architecture Overview

### Dual-Server and Dual-Model Architecture
bapXcoder implements a sophisticated architecture combining both dual-server and dual-model approaches:

**Server Architecture:**
- **Frontend Server** (hosted on Hostiger): Handles authentication, payments, and landing page
- **Local Application** (downloaded by users): Full IDE functionality with llama.cpp runtime model connections

**AI Model Architecture:**
- **Interpreter Model (bapXcoder-Interpreter)**: Handles communication, UI understanding, multimodal processing, OCR, and user interactions
- **Developer Model (bapXcoder-Developer)**: Specializes in coding tasks, code generation, analysis, and implementation
- **Direct Hugging Face Connection**: Both models connect via llama.cpp runtime
- **Quota-Based Operation**: Uses your allocated runtime quotas for both models

## Why This Architecture Matters
Most AI IDEs use a single model that directly interacts with users. This creates issues:
- Hallucinations and inconsistent responses
- Lost context between sessions
- Poor project awareness
- No safety checks

bapXcoder uses a deterministic pipeline:
- **Interpreter** (bapXcoder-Interpreter) receives all user input and maintains context
- **Developer** (bapXcoder-Developer) only executes structured instructions from Interpreter
- No direct user-to-Developer communication prevents inconsistency
- Session persistence maintained through Interpreter model

## Visual Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input   │───▶│  Interpreter     │───▶│   Developer     │
│                │    │  Model (bapXcoder-Interpreter)│    │  Model (bapXcoder-  │
│ (Natural       │    │ • Context        │    │   Developer)   │
│  Language)     │    │ • Communication  │    │ • Code Gen     │
│                │    │ • Multimodal     │    │ • Implementation│
└─────────────────┘    │ • Instructions   │    │ • Execution    │
                      └──────────────────┘    └─────────────────┘
                             │
                        ┌─────────────┐
                        │  Project    │
                        │  Context    │
                        │  (.bapXcoder)│
                        └─────────────┘
```

## Models Documentation & Images

### bapXcoder-VL (Interpreter Model)
The bapXcoder-VL model provides the interpretation layer of bapXcoder:

![bapXcoder-VL Model Architecture](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-Coder/qwen3_coder.png)

**Key Capabilities**:
- Multimodal understanding (text, images, GUI elements)
- OCR with 32+ language support
- Context management across sessions
- User communication and instruction generation

### bapXcoder-Coder (Developer Model)
The bapXcoder-Coder model provides the specialized coding capabilities:

![bapXcoder-Coder Model Architecture](https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-Coder/qwen3-coder-main.jpg)

**Key Capabilities**:
- Specialized code generation and analysis
- Implementation of structured instructions
- Code optimization and debugging
- Repository-level understanding for coding tasks

## Resources Documentation & Images

### Resource: Qwen-Code CLI
The `resources/qwen-code/` folder contains reference implementations for CLI-first AI development:

![Qwen Code Interface](https://cdn.prod.website-files.com/664efefb6c6ed1d4cfdf82da/66a0d30c52b9523bea3306d0_gemini-cli.png)

**Used for**:
- Reference for CLI workflow patterns
- Direct model connection approaches
- Terminal-based AI interaction patterns

### Resource: Codespaces Base
The `resources/codespaces-base/` folder contains reference for development environment patterns:

![Codespaces Environment](https://github.blog/wp-content/uploads/2021/08/feature-panorama-full.png?resize=1200%2C600)

**Used for**:
- Reference for development environment concepts
- UI integration patterns
- Extension and tooling approaches

## Comparison with Other Tools

| Feature | bapXcoder | Continue.dev | Antigravity IDE |
|---------|-------------|----------------|------------------|
| **Operation** | Dual-model with llama.cpp runtime (similar to Cursor/Continue) | Hybrid (local LLMs) | Cloud-based |
| **Cost** | License-based with 60-day trial | Subscription | Pay-per-use |
| **Privacy** | Project data local, session intelligence persists locally via llama.cpp | Local processing | Data goes to cloud |
| **Model** | Dual-model: Interpreter (bapXcoder-VL) for UI/communication + Developer (bapXcoder-Coder) for coding via llama.cpp runtime | Multiple configurable models | Various cloud models |
| **AI Capability** | Vision, OCR, text, code with dual-model specialization | Text completion | Text completion |
| **Connectivity** | Requires internet for runtime access | Needs cloud API keys | Requires internet for runtime access |
| **Customization** | Project-based memory system with dual-model coordination | VS Code extensions | Browser-based |

## Technical Implementation Details

### Dual-Model Architecture
The system implements a strict separation of concerns:

1. **User Communication Layer**: Interpreter model (bapXcoder-VL) handles all user input/output
2. **Instruction Generation**: Interpreter converts user intent into structured developer instructions
3. **Code Execution Layer**: Developer model (bapXcoder-Coder) executes only structured instructions
4. **Response Mediation**: All responses go back through Interpreter model to user

### Session Persistence
- Each project maintains its own `.bapXcoder` directory
- `todo.json` for project-specific task tracking
- `sessiontree.json` for session-based activity tracking
- Context persists between sessions for each project

### File Operation Safety
- All file operations mediated through Interpreter model
- Changes are structured as instructions to Developer model
- Atomic operations with preview before execution
- Project boundary validation to ensure operations stay within project scope

## Troubleshooting

### Common Issues

1. **Model Connection Issues**: Verify your quota access to Qwen models via llama.cpp runtime
2. **Audio Issues**: Check microphone permissions for STT and speaker settings for TTS
3. **File Access Errors**: Ensure sufficient permissions for project directory operations
4. **Network Issues**: Verify internet connection for model runtime access

### Performance Optimization

1. **RAM Usage**: Ensure at least 8GB RAM for optimal performance
2. **GPU Acceleration**: Configure llama.cpp for GPU acceleration if available
3. **Project Size**: Keep projects appropriately sized for optimal AI processing
4. **Context Management**: Use project-based organization to maintain focused context

## License & Usage Model

### Subscription & Licensing Model
- **Trial Period**: 60 days of full access to all features
- **Monthly License**: $1 per month for ongoing access
- **Lifetime License**: $100 one-time payment for perpetual access
- **Secure Storage**: All subscription data encrypted and stored in user's GitHub repositories
- **No Recurring Charges**: After lifetime license purchase, no further costs
- **Privacy Protection**: No user code stored on our servers - only encrypted metadata in GitHub

## Contributing

This project welcomes contributions! If you'd like to help enhance bapXcoder:

- Report bugs or suggest features
- Contribute code improvements
- Help with documentation
- Share your use cases and feedback
- Improve multimodal processing capabilities

## Architecture Overview

The bapXcoder IDE leverages a dual-model architecture with Interpreter model (bapXcoder-VL) for user communication and context management, and Developer model (bapXcoder-Coder) for specialized coding tasks, providing a comprehensive development environment:

### Core AI Capabilities:
- **Interpreter Model (bapXcoder-VL)**: Handles user communication, multimodal processing, OCR, voice input/output, web research, and attaches file analysis for images
- **Developer Model (bapXcoder-Coder)**: Executes coding tasks, code generation, and code analysis based on structured instructions from Interpreter
- **Dual-Model Pipeline**: All user prompts go to Interpreter; Developer executes only structured instructions from Interpreter, never seeing user directly
- **Structured Instruction System**: Interpreter converts user intent into specific instructions for Developer model execution
- **File Analysis**: Interpreter handles image/document analysis; Developer handles code analysis and execution
- **Mediated Coordination**: Interpreter manages communication and project state, issuing specific instructions to Developer model

### Web Interface Integration:
- **Landing Page**: Marketing and authentication interface hosted on Hostinger
- **GitHub Integration**: Secure OAuth authentication with encrypted data storage
- **Payment Processing**: Stripe integration for subscription management
- **Download Management**: Authorized downloads only after subscription validation

### Project-Based Memory System:
- **Persistent Context**: Unlike cloud IDEs that lose session context, bapXcoder maintains project-specific memory with `.bapXcoder` directories
- **File-Level Association**: Todos, session trees, and conversation history are tied to individual projects, maintaining focused context
- **Local Session Memory**: Only session + RAG context lives locally in `.bapXcoder` directories
- **Cross-File Understanding**: The AI remembers relationships between files in your project, providing better contextual suggestions
- **Long-Term Learning**: The system improves its understanding of your codebase over time within each project

### Advanced CLI Integration:
- **Integrated Terminal**: Built-in command line interface within the web IDE
- **Direct CLI Operations**: All functionality executed via CLI commands underneath the web UI
- **Project Context**: Commands execute within the current project directory
- **Git Integration**: Full Git operations with OAuth support via CLI
- **File Operations**: Direct file manipulation through CLI operations, with web UI providing convenience layer
- **System Integration**: All system interactions handled via terminal commands at the backend

## Phase-Based Auto Execution & Testing
- **AI-Driven Testing System**: Interpreter model (bapXcoder-VL) coordinates comprehensive validation that validates code after each change
- **Individual File Testing**: Each file tab has its own "Test & Validate File" button (play icon)
- **Project-Wide Validation**: "Validate Full Project" button for complete project analysis
- **Phase-Based Execution**: System tracks validation history and project phases through sessiontree.json
- **Run Primary Project File**: Left sidebar menu includes run buttons for executing primary project files
- **AI-Integrated Testing**: Interpreter model mediates interactions with AI to execute tests from the test folder

## Resources Integration

As mentioned, the `resources/` folder contains valuable reference implementations that informed the development of bapXcoder:

- **Qwen Code Resources**: Reference for CLI workflow patterns and direct model connections
- **bapXcoder-Coder Resources**: Reference for advanced coding model capabilities
- **Codespaces Resources**: Reference for development environment concepts
- **Hugging Face Connection Documentation**: Approaches for direct model access without local downloads

These serve as valuable references for understanding implementation patterns but are separate from the main application.

## Why This Approach Works Better Than Single-Model IDEs

1. **Deterministic Behavior**: Predictable responses since all processing goes through Interpreter
2. **Safety**: Developer model only executes verified instructions, preventing unsafe operations
3. **Context Consistency**: Interpreter model maintains consistent project context
4. **Specialization**: Each model focuses on its specific role for optimal performance
5. **Session Persistence**: Context is maintained between sessions through Interpreter model

## Advanced Features

### Multimodal Processing
The Interpreter model (bapXcoder-VL) handles all multimodal inputs:
- Image analysis with OCR capabilities
- Document understanding with layout preservation
- Visual GUI element recognition
- Spatial relationship understanding

### Code Generation Pipeline
The Developer model (bapXcoder-Coder) handles all coding tasks:
- Code generation based on structured requirements
- Code analysis and optimization
- Implementation of specific developer instructions
- Repository-level code understanding

### Project Memory System
Each project gets its own dedicated memory context:
- Session persistence across restarts
- Task management with project-specific to-do lists
- File association and context tracking
- Long-term learning about project structure

## Performance Considerations

1. **Model Runtime**: Requires internet connection for llama.cpp runtime access
2. **Memory Requirements**: Recommended 8GB+ RAM for optimal performance
3. **Project Organization**: Well-structured projects perform better with AI assistance
4. **File Sizes**: Large files may impact processing performance

## Security & Privacy

- All project data remains on the user's local machine
- Model interactions happen through runtime connection (not stored locally)
- No user code is transmitted to external servers
- Session encryption for sensitive metadata
- Local file operation permissions respected at OS level

## Support & Community

For support, questions, or to report issues, please use the GitHub repository issues section. The community is growing and we welcome feedback, suggestions, and contributions.

---

## About the Underlying Models

The dual-model system powering bapXcoder connects to Qwen3-VL and Qwen3-Coder models through the llama.cpp runtime integration. These models are compatible with llama.cpp runtime, supporting inference on CPU, NVIDIA GPU (CUDA), Apple Silicon (Metal), Intel GPUs (SYCL), and more. You can mix precisions for optimal performance.

The system leverages Alibaba Cloud's open-source Qwen models to provide advanced AI capabilities locally without cloud dependencies.

## Project Status

### Current Version
- **Stable Release**: v1.0 (Current)
- **Next Release**: v1.1 (In Development)

### Feature Completeness
- [x] Core IDE Functionality
- [x] AI-Powered Code Assistance
- [x] Project-Based Memory System
- [x] Web-Based Interface
- [x] Hugging Face Model Connection
- [x] Cross-Platform Support
- [x] Single-File Installer
- [x] Documentation

### Planned for v1.1
- [ ] Enhanced UI/UX
- [ ] Additional Language Support
- [ ] Performance Improvements
- [ ] Advanced Validation Features

## Landing Page

A professional landing page is available at `https://getwinharris.github.io/bapXcoder/` featuring:
- Clean, modern design similar to Cursor IDE
- Clear download CTA in center of page (after license acquisition)
- Focus on project memory and AI capabilities
- Emphasizes dual-model architecture with licensing model (no $20/mo like other tools)
- Professional presentation for developer adoption
