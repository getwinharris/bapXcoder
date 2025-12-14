# bapX Coder - User-Facing Behaviors Documentation

## Overview
bapX Coder is an AI-powered Integrated Development Environment (IDE) that runs locally with persistent project memory. The system combines a web-based UI with local AI processing to provide an offline-capable development environment.

## Core User Behaviors

### 1. Installation & Setup
- **Single File Installation**: Download and run `bapXvector.sh` to install the entire system
- **Automatic Dependency Check**: System checks for Python 3.8+, Git, and other required tools
- **Model Download**: Automatically downloads the Qwen3VL model (~8.76GB) in the background
- **System Integration**: Creates shortcuts and sets up auto-start options
- **Web Interface Launch**: Automatically opens the IDE in your default browser at `http://localhost:7860`

### 2. Project Management
- **Project Initialization**: Set project path to enable project-based memory
- **Persistent Context**: Each project maintains its own `.bapXcoder` directory with session data
- **Session Continuity**: All project state (open files, todos, AI context) preserved across sessions
- **File Explorer**: Navigate project files with tree view and file icons
- **Multi-Project Support**: Switch between different projects maintaining separate contexts

### 3. AI-Powered Interactions
- **Chat Interface**: Natural language conversation with the Qwen3VL AI model
- **Code Assistance**: Real-time coding help and suggestions with context awareness
- **File Attachment**: Attach files for AI analysis (code, images, documents)
- **Image Analysis**: OCR and visual processing when images are attached
- **Web Search**: Integrated web search functionality within the chat interface
- **Voice Input/Output**: Speech-to-text for input and TTS for auto-play responses
- **Continue Reasoning**: Extend long conversations beyond context window

### 4. Code Editing & Analysis
- **Code Editor**: Syntax-highlighted editor with Monaco editor backend
- **File Tabs**: Multiple file tabs with individual run buttons
- **File Validation**: Individual file validation with "Test & Validate" button
- **Project Validation**: Full project validation with "Validate Full Project" button
- **Live Syntax Checking**: Real-time syntax validation (S:✓/✗, U:✓/✗, F:✓/✗ indicators)
- **AI Analysis**: Security checks, performance analysis, and code quality suggestions

### 5. Terminal & Command Execution
- **Integrated Terminal**: Built-in command line interface within the IDE
- **Project Context**: Commands execute within the current project directory
- **Command Approval**: Request approval for potentially destructive commands
- **Git Integration**: Full Git operations with OAuth support
- **Command History**: Track executed commands

### 6. Task Management
- **Project-Specific Todos**: Each project maintains its own todo list in `todo.json`
- **Priority Tracking**: Todo items with priority and completion status
- **Session Tracking**: Activity logs preserved per project session
- **Progress Tracking**: Track completion of development objectives

### 7. File Operations
- **File Creation**: Create new files and directories from the UI
- **File Editing**: Edit code with syntax highlighting and AI suggestions
- **File Search**: Search across project files with extension filtering
- **File Validation**: Per-file syntax and security validation
- **File Monitoring**: Auto-detection of file changes

### 8. Validation & Testing
- **Individual Testing**: Individual "Test & Validate File" button for each file
- **Project-Wide Testing**: Comprehensive validation of entire codebase
- **Status Indicators**: Concise status indicators (S: syntax, U: unit tests, F: functional tests)
- **Complexity Scoring**: C:X/10 scoring for code complexity
- **Security Monitoring**: Sec:X counting security issues
- **Performance Monitoring**: Perf:X counting performance issues
- **Suggestion Counting**: Sug:X counting AI suggestions

### 9. UI Navigation & Controls
- **4-Panel Layout**: Explorer, Options, Editor, and Chat/Terminal panels
- **Sidebar Navigation**: Explorer, Search, Git, Run, Debug, Extensions panels
- **File Tab Management**: Open, close, and switch between multiple files
- **Run Buttons**: Individual run buttons for each file and project-wide run
- **Save Functionality**: Manual and auto-save options
- **Theme Management**: Dark theme with purple accent colors

### 10. System Integration
- **PWA Installation**: Installable on devices as a native application
- **Offline Functionality**: Complete offline operation after setup
- **Local Processing**: All AI processing happens locally with no cloud dependencies
- **Cross-Platform**: Works identically on Mac, Windows, and Linux
- **Browser Access**: Accessible through any modern web browser

### 11. Security & Privacy
- **Local Data Processing**: All code and conversations stay on local machine
- **No Cloud Dependencies**: No internet required after initial setup
- **Model Privacy**: Qwen3VL model runs entirely locally
- **Project Isolation**: Each project's context is isolated from others

### 12. Performance & Optimization
- **Resource Management**: Efficient memory and CPU usage by local model
- **Background Processing**: Model operations don't block UI interactions
- **Context Management**: Smart context preservation without memory leaks
- **File Caching**: Efficient file access and caching mechanisms

## User Workflow Examples

### New Project Setup
1. Download and run `bapXvector.sh`
2. Set project directory in the IDE
3. Begin coding with AI assistance
4. All context preserved across sessions

### Code Development Cycle
1. Open/create files in the editor
2. Ask AI for coding assistance via chat
3. Validate individual files with "Test & Validate"
4. Run code with file-specific run buttons
5. Use integrated terminal for additional operations
6. All changes and context preserved automatically

### AI-Assisted Debugging
1. Describe the problem to the AI in chat
2. Attach relevant files for analysis
3. Receive context-aware suggestions
4. Implement fixes with AI guidance
5. Validate changes with automated testing
6. Track progress in project-specific todos

## Error Handling & Recovery
- **Model Availability**: Automatic download if model is missing
- **Dependency Checks**: Verify all required tools are available
- **Session Recovery**: Restore session state if IDE is restarted
- **Error Reporting**: Clear error messages for debugging
- **Graceful Degradation**: Maintain core functionality if some features fail