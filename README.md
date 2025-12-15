# bapXcoder - Advanced AI-Powered PWA IDE

**bapXcoder** is a revolutionary, cross-platform PWA (Progressive Web App) Integrated Development Environment that combines the power of dual AI models into a single, deterministic development environment. Unlike traditional AI tools that lose context or operate in fragments, bapXcoder maintains persistent project memory and executes tasks through a sophisticated interpreter-developer model architecture.

## What Problem Does bapXcoder Solve?

### The Fragmentation Problem
Modern AI development tools suffer from fundamental issues:
- **Context Loss**: Most tools lose session state between uses
- **Model Limitations**: Single-model tools can't specialize effectively
- **Fragmented Workflow**: Different tools for different tasks create context switching
- **Privacy Concerns**: Cloud-based tools transmit code to external servers
- **Limited Autonomy**: Most tools require constant user oversight

### bapXcoder's Solution
- **Persistent Project Memory**: Every project maintains its own context with `.bapXcoder` directories
- **Dual-Model Intelligence**: Interpreter model handles communication while Developer model handles coding
- **Deterministic Execution**: Predictable, safe execution with change previews
- **Complete Privacy**: All project data stays local; only model access happens externally
- **Autonomous Modes**: YOLO/Autonomous execution for complex tasks

## Key Capabilities

### Deterministic AI Interaction
- **Interpreter Model**: Handles all user communication, multimodal processing, OCR, and context management
- **Developer Model**: Executes only structured instructions from Interpreter, never communicating directly with user
- **Safe Execution**: All changes shown as diffs before approval
- **Project Context**: Maintains awareness of entire codebase for accurate suggestions

### Advanced AI Features
- **Multimodal Processing**: OCR, image analysis, document understanding with 32+ language support
- **Voice I/O**: Speech-to-text for input and text-to-speech for auto-play output
- **Web Research**: Integrated search with AI-powered result processing
- **File Analysis**: Attach and analyze code, image, and document files directly

### Session Persistence
- **Project-Based Memory**: Each project gets its own `.bapXcoder` directory with persistent `todo.json` and `sessiontree.json`
- **Task Management**: Project-specific to-do lists with priority and completion tracking
- **Cross-Session Awareness**: Context maintained between sessions within each project
- **Long-Term Learning**: System improves understanding of your codebase over time within each project

## How to Get Started

Simply run the following command to start bapXcoder:

```bash
./coder.bapx
```

For detailed technical documentation, architecture details, and development information, see our [internal documentation](./doc.md).

## Why bapXcoder is Different

Unlike other AI IDEs that struggle with context, bapXcoder provides:
- **Complete Project Understanding**: Maintains full codebase context during development
- **Predictable Results**: Deterministic behavior through interpreter-developer model separation
- **Safe Operations**: Preview all changes before applying with diff visualization
- **Privacy-First**: All project data remains local; only model interactions happen externally
- **Autonomous Execution**: Advanced YOLO/Autonomous modes for complex task execution

## Learn More

Visit our website: [coder.bapx.in](https://coder.bapx.in)

## License

This project is available under a proprietary license model with a 60-day trial period. After the trial, a license is required for continued use.