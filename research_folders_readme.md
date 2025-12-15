# Research Folders - Reference Documentation

## Overview

This document clarifies the purpose and status of the research folders in this repository. These folders contain external projects and references that were used during the development of bapX Coder but are NOT part of the main application distribution.

## Research Folders Status

### research/qwen-code/
- **Source**: https://github.com/QwenLM/qwen-code
- **Purpose**: Reference for CLI workflow patterns and Qwen model optimization
- **Status**: RESEARCH REFERENCE ONLY - Not part of main application
- **Used for**: Understanding CLI-first approaches and Qwen model integration patterns

### research/Qwen3-Coder/  
- **Source**: https://github.com/QwenLM/Qwen3-Coder
- **Purpose**: Reference for advanced coding capabilities and model features
- **Status**: RESEARCH REFERENCE ONLY - Not part of main application
- **Used for**: Understanding specialized coding model capabilities

### research/codespaces-base/
- **Source**: https://github.com/codespaces-examples/BASE
- **Purpose**: Reference for development environment concepts
- **Status**: RESEARCH REFERENCE ONLY - Not part of main application
- **Used for**: Understanding cloud-based development environment patterns

### research/qwen3-vl-hf/
- **Purpose**: Documentation about direct Hugging Face connections
- **Status**: RESEARCH REFERENCE ONLY - Not part of main application
- **Used for**: Understanding connection methodologies

### research/*.md files
- **Purpose**: Analysis and comparison documents
- **Status**: RESEARCH REFERENCE ONLY - Not part of main application
- **Used for**: Architectural decision making and feature planning

## Main Application Components

The actual bapX Coder application consists of:

### Core Files:
- qwen3VL_local_cli.py
- project_explorer.py  
- syntax_checker.py
- validation_system.py
- encoding_utils.py
- config.ini
- requirements.txt

### Web Interface:
- templates/index.html
- templates/manifest.json
- admin_panel.html

### Documentation (Main Project):
- README.md (updated)
- LICENSE
- features_comparison.md
- USER_BEHAVIORS.md
- docs/

## Important Distinction

- **Main Application**: The actual bapX Coder IDE with dual-model architecture
- **Research Folders**: External repositories used as reference during development

The research folders are included to provide context for development decisions and architectural choices, but they are not distributed with or required by the main application.

## Business Model Clarification

The main bapX Coder application:
- Uses a licensing model (60-day trial, then license required)
- Connects directly to Hugging Face models using allocated quotas
- Implements dual-model architecture (Qwen3-VL for communication, Qwen3-Coder for coding)
- Requires internet connectivity for model access
- Maintains project-based memory with .bapXcoder directories

The research references were used to inform these architectural decisions but are not part of the commercial product.