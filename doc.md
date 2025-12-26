# bapXcoder Development Documentation

## Internal Architecture Overview

The bapXcoder IDE implements a sophisticated single-agent architecture with internal role separation. This design prioritizes deterministic behavior, user control, and persistent project context over magical functionality.

### Core Architecture Principles

1. **Single IDE Agent**: Instead of multiple models, one unified agent with internal coordination
2. **Internal Role Separation**: Two specialized functions within single agent:
   - Interpreter Function: Handles user communication and context management
   - Developer Function: Executes specialized coding tasks
3. **Shared Session Memory**: Both functions access same project context through `.bapXcoder` system
4. **Deterministic Execution**: Predictable responses with clear role boundaries

### Project-Based Session Memory System

**Files Structure:**
- `.bapXcoder/users/{user_id}/sessiontree.json` - Session state and memory (session continuity)
- `.bapXcoder/users/{user_id}/todo.json` - User intent and task tracking
- `.bapXcoder/users/{user_id}/validation_log.json` - AI-driven testing results

**How Continuity Works:**
1. On startup, CLI checks `.bapXcoder/users/{user_id}/sessiontree.json`
2. Reads: "last task", "last action", "pending tasks" from sessiontree.json and todo.json
3. Constructs message: "System resumed. You were working on X. Last action was Y. Pending tasks: Z."

### Internal Functions Documentation

#### BapXcoderIDEAgent class functions:

**`def __init__(self, model_path=None, temperature=0.7, threads=4, context_size=4096, gpu_layers=0):`**
- Initialize the bapXcoder IDE Agent with Interpreter and Developer models
- Sets up internal agent with two specialized models working through shared memory
- Connects to Qwen3-VL for interpreter function and Qwen3-8B for developer function

**`def run_prompt(self, prompt, max_tokens=512, check_session_on_startup=False):`**
- Process user prompt through the bapXcoder IDE Agent's Interpreter function
- If check_session_on_startup=True, prepends session continuity info to prompt
- Handles all user communication, context management, and multimodal processing

**`def check_session_continuity(self):`**
- Checks session state and memory from .bapXcoder/users/{user_id}/sessiontree.json
- Reads user intent from .bapXcoder/users/{user_id}/todo.json
- Returns continuity message for context restoration

**`def run_coding_task(self, task_description, max_tokens=512):`**
- Execute specialized coding task through bapXcoder IDE Agent's Developer function
- Handles code generation, refactoring, and analysis via specialized coding model

### Memory and Session Management

**User-Specific Directories:**
- `.bapXcoder/users/{user_id}/` - Contains user-specific session data
- Separate session memory per user per project (multi-user isolation)

**Functions:**
- `store_sessiontree_data()` - Updates session state and memory in sessiontree.json
- `store_todo_locally()` - Updates user intent in todo.json
- `check_user_session_continuity()` - Checks both sessiontree.json and todo.json for continuity

### Authentication and User System

**User Verification:**
- JWT token validation for user authentication
- User-ID verification through authentication headers
- Subscription status checked per user account

**Session Continuity:**
- Triggered on user connect via socket handlers
- Emits 'session_continuity' events to client
- Restores project context based on user-specific files

### File Operations and Project Management

**Project Explorer:**
- Handles file system navigation
- Manages project directory structure
- Maintains file statistics and recent file tracking

**File Management:**
- All operations happen through CLI backend
- Web UI provides convenience layer over CLI operations
- Project-based file operations in user context

### Model Integration

**Dual-Model Architecture:**
- Interpreter Model: Qwen3-VL for communication, UI, multimodal processing
- Developer Model: Qwen3-Coder for coding tasks and analysis
- Both models connected via llama.cpp runtime without local download

**Runtime Connection:**
- Direct connection to Hugging Face via llama.cpp
- No local model storage required
- Quota-based access through runtime connections

### Technical Implementation

**Key Dependencies:**
- llama-cpp-python: For model inference
- flask/flask-socketio: For web interface and real-time communication
- jwt: For authentication
- huggingface_hub: For model access

**Safety Measures:**
- All code changes require user approval
- Diff visualization before application
- Role isolation between interpreter and developer functions
- Boundary enforcement within project scope

### Event System

**Socket.IO Handlers:**
- `connect`: Checks user authentication and session continuity
- `chat_message`: Processes messages through dual-model system
- `add_todo`: Updates user intent in todo.json
- Various file and project management events

### Error Handling and Fallbacks

- Graceful degradation when models unavailable
- Fallback to same model for both functions if specialized model fails
- Local session data preserved when connection lost
- User-specific data isolation maintained during errors

This comprehensive architecture ensures deterministic behavior, persistent project memory, and seamless session continuity for maximum time-saving and productivity.