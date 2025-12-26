# bapXcoder Architecture Summary

## Project Overview
bapXcoder is now properly documented as a dual-model AI-powered IDE with:

1. **bapXcoder-VL Model**: Handles communication, UI understanding, multimodal processing, OCR, and user interactions
2. **bapXcoder-Coder Model**: Specializes in coding tasks, code generation, analysis, and implementation
3. **Direct Model Access via llama.cpp**: Both models connect via llama.cpp runtime without local downloads
4. **Runtime-Based Operation**: Uses llama.cpp runtime for both models

## Changes Made

### README.md Updates
- Updated to reflect dual-model architecture instead of single model
- Changed from "local downloads" to "runtime access" terminology
- Updated licensing model to reflect 60-day trial then license requirement
- Removed references to "completely free" and updated to accurate licensing model
- Added comparison with Cursor/Continue-like architecture

### Code Documentation
- Added concise two-line documentation above each function
- Documented the dual-model coordination architecture
- Updated internal file operation documentation

### Research Folders
- Clearly marked as "RESEARCH REFERENCES ONLY" in documentation
- Added proper gitignore entries to exclude embedded git repositories
- Created documentation explaining their purpose as development references

## Key Architecture Features

1. **Repo-aware**: Maintains comprehensive context of the entire codebase
2. **Session-persistent**: Remembers state, todos, and conversation history across sessions  
3. **Local-memory**: Session and RAG context stored locally in .bapXcoder directories
4. **PWA-accessible**: Works across all platforms as an installable application
5. **Runtime-based**: Uses llama.cpp as the runtime for model access
6. **Deterministic behavior**: Interpreter model handles all user interaction while Developer model specializes in coding

## Dual-Model Workflow
- User interacts with bapXcoder-VL (Interpreter) model through the interface
- Interpreter manages project state and context
- bapXcoder-Coder (Developer) model executes specialized coding tasks based on instructions from Interpreter
- All model access happens via direct llama.cpp runtime connection

## Licensing Model
- 60-day trial period
- 30-day subscription ($1 every 30 days) after trial
- Lifetime license ($100 one-time) for perpetual access
- Session intelligence persists locally via llama.cpp runtime access

The repository now accurately reflects the sophisticated dual-model architecture while clearly distinguishing between the main application and research reference materials.