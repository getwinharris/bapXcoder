# bapXcoder - Advanced AI-Powered PWA IDE

**bapXcoder** is a revolutionary, cross-platform PWA (Progressive Web App) Integrated Development Environment featuring the single "bapXcoder" IDE Agent. This deterministic CLI-first development environment uses one powerful AI agent with internal role separation: an interpreter for user communication and context management, and a developer for coding tasks. Unlike traditional AI tools that lose context or operate in fragments, bapXcoder maintains persistent project memory and executes tasks through a sophisticated internal agent with shared session memory.

## What Problem Does bapXcoder Solve?

### The Fragmentation Problem
Modern AI development tools suffer from fundamental issues:
- **Context Loss**: Most tools lose session state between uses
- **Single-Agent Limitations**: Single-model tools can't specialize effectively
- **Fragmented Workflow**: Different tools for different tasks create context switching
- **Privacy Concerns**: Cloud-based tools transmit code to external servers
- **Limited Autonomy**: Most tools require constant user oversight

### bapXcoder's Solution
- **Persistent Project Memory**: Every project maintains its own context with `.bapXcoder` directories
- **Single IDE Agent**: One AI agent with internal role separation between interpreter and developer functions
- **Deterministic Execution**: Predictable, safe execution with change previews
- **Complete Privacy**: All project data stays local; only model access happens externally
- **Autonomous Modes**: Advanced autonomous execution for complex tasks

## Core Architecture: Single Agent with Dual Roles

bapXcoder implements a unique single-agent architecture with internal role separation:

### The bapXcoder IDE Agent
- **Single Agent**: One unified AI agent (not multiple models) that handles all development tasks
- **Internal Role Separation**: Two internal functions working together:
  - **Interpreter Function**: Handles all communication, UI understanding, multimodal processing, OCR, and context management
  - **Developer Function**: Executes only structured instructions from interpreter, following internal workflow protocols
- **Shared Session Memory**: Both functions share the same project context through `.bapXcoder` session tree
- **Authoritative Memory**: Single source of truth for project state and todos across both functions

### How It Works
1. **User interacts with Agent**: All prompts go to the single IDE Agent
2. **Interpreter processes request**: Interpreter function understands the request and context
3. **Developer executes if needed**: If coding is required, interpreter coordinates with developer function
4. **Agent responds to user**: Single response back to user through interpreter
5. **Memory persists**: Both functions update shared session memory (`.bapXcoder/sessiontree.json`, `.bapXcoder/todo.json`)

## Key Capabilities

### Deterministic AI Interaction
- **Interpreter Function**: Handles all user communication, multimodal processing, OCR, and context management
- **Developer Function**: Executes only structured instructions from interpreter, following internal workflow protocols  
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

### Why This Architecture Matters
- **No Hallucinations**: Interpreter maintains authoritative context, Developer only executes authorized changes
- **Safe Operations**: All code changes go through interpreter's approval process
- **Consistent Behavior**: Single agent ensures consistent responses and context
- **Role Separation**: Clear separation between communication and coding tasks for safety
- **Shared Memory**: Both functions access the same project context for consistency

## How to Get Started

Simply run the following command to start bapXcoder:

```bash
./coder.bapx
```

For detailed technical documentation, architecture details, and development information, see our [internal documentation](./doc.md).

## Why bapXcoder is Different

Unlike other AI IDEs that struggle with context, bapXcoder provides:
- **Complete Project Understanding**: Maintains full codebase context during development
- **Predictable Results**: Deterministic behavior through interpreter-developer role separation within a single IDE Agent
- **Safe Operations**: Preview all changes before applying with diff visualization
- **Privacy-First**: All project data remains local; only model interactions happen externally
- **Autonomous Execution**: Advanced autonomous modes for complex task execution

## Learn More

Visit our website: [coder.bapx.in](https://coder.bapx.in)

## License

This project is available under a proprietary license model with a 60-day trial period. After the trial, a license is required for continued use.