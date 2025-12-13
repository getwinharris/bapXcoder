#!/usr/bin/env python3
"""
qwen3VL-Local-CLI: A command-line interface for running Qwen3VL model locally
"""

import argparse
import sys
import os
from pathlib import Path
import configparser

def load_config():
    """Load configuration from config.ini file"""
    config = configparser.ConfigParser()
    config_path = Path("config.ini")

    if config_path.exists():
        config.read(config_path)
        return config
    else:
        # Return default values if config doesn't exist
        config['model'] = {'model_path': 'Qwen3VL-8B-Instruct-Q8_0.gguf'}
        config['defaults'] = {
            'max_tokens': '512',
            'temperature': '0.7',
            'threads': '4',
            'context_size': '4096',
            'gpu_layers': '0'
        }
        return config

def main():
    config = load_config()

    # Get default values from config
    default_model_path = config.get('model', 'model_path', fallback='../Qwen3VL-8B-Instruct-Q8_0.gguf')
    default_max_tokens = config.getint('defaults', 'max_tokens', fallback=512)
    default_temperature = config.getfloat('defaults', 'temperature', fallback=0.7)

    # Check if the model file exists at the specified location
    model_path = Path(default_model_path).resolve()
    if not model_path.exists():
        # Try alternative locations
        model_path = Path("../Qwen3VL-8B-Instruct-Q8_0.gguf").resolve()
        if not model_path.exists():
            model_path = Path("Qwen3VL-8B-Instruct-Q8_0.gguf")
            if not model_path.exists():
                print(f"Error: Model file not found at {default_model_path} or in standard locations")
                sys.exit(1)

    parser = argparse.ArgumentParser(description="qwen3VL-Local-CLI: Run Qwen3VL model locally")
    parser.add_argument("--model", type=str, default=str(model_path), help="Path to the GGUF model file")
    parser.add_argument("--prompt", type=str, help="Direct prompt to send to the model")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive chat mode")
    parser.add_argument("--max-tokens", type=int, default=default_max_tokens, help="Maximum tokens to generate")
    parser.add_argument("--temperature", type=float, default=default_temperature, help="Sampling temperature")
    parser.add_argument("--threads", type=int, default=config.getint('defaults', 'threads', fallback=4), help="Number of CPU threads")
    parser.add_argument("--context-size", type=int, default=config.getint('defaults', 'context_size', fallback=4096), help="Context size in tokens")
    parser.add_argument("--gpu-layers", type=int, default=config.getint('defaults', 'gpu_layers', fallback=0), help="Number of GPU layers (0 for CPU only)")
    parser.add_argument("--help-model", action="store_true", help="Show model configuration help")

    args = parser.parse_args()

    if args.help_model:
        print_help()
        return

    if not args.prompt and not args.interactive:
        print("Please provide a prompt or use -i for interactive mode")
        parser.print_help()
        return

    # Initialize the local model runner
    runner = Qwen3VLRunner(
        args.model,
        args.temperature,
        args.threads,
        args.context_size,
        args.gpu_layers
    )

    if args.interactive:
        runner.run_interactive(args.max_tokens)
    else:
        response = runner.run_prompt(args.prompt, args.max_tokens)
        print(response)

def print_help():
    print("""
qwen3VL-Local-CLI - Configuration Guide
=======================================

This CLI tool allows you to run the Qwen3VL model locally using llama.cpp.
Repository: https://github.com/getwinharris/qwen3VL-Local-CLI

Prerequisites:
1. Install llama.cpp: pip install llama-cpp-python
2. Install this tool: pip install -e .
3. Have your model file: Qwen3VL-8B-Instruct-Q8_0.gguf (included in repo)

Basic Usage:
  python qwen3VL_local_cli.py --prompt "Hello, how are you?"
  python qwen3VL_local_cli.py -i  # Interactive mode
  python qwen3VL_local_cli.py --model /path/to/model.gguf --prompt "Your prompt"

Options:
  --model PATH          Path to GGUF model file (default: Qwen3VL-8B-Instruct-Q8_0.gguf)
  --prompt TEXT         Direct prompt to send to the model
  --interactive, -i     Start interactive chat mode
  --max-tokens N        Maximum tokens to generate (default: 512)
  --temperature T       Sampling temperature (default: 0.7)
  --threads N           Number of CPU threads (default: 4)
  --context-size N      Context size in tokens (default: 4096)
  --gpu-layers N        Number of GPU layers (0 for CPU only, default: 0)
  --help-model          Show this help message

Examples:
  # Simple prompt
  python qwen3VL_local_cli.py --prompt "Explain quantum computing in simple terms"

  # Interactive chat
  python qwen3VL_local_cli.py -i

  # With custom parameters
  python qwen3VL_local_cli.py --prompt "Write a poem" --temperature 0.9 --max-tokens 1024

  # Using GPU acceleration
  python qwen3VL_local_cli.py --prompt "Hello!" --gpu-layers 20
    """)

class Qwen3VLRunner:
    def __init__(self, model_path, temperature=0.7, threads=4, context_size=4096, gpu_layers=0):
        self.model_path = model_path
        self.temperature = temperature
        self.threads = threads
        self.context_size = context_size
        self.gpu_layers = gpu_layers
        self.model = None
        self.chat_history = []

        # Try to import llama-cpp-python
        try:
            from llama_cpp import Llama
            self.Llama = Llama
        except ImportError:
            print("Error: llama-cpp-python is not installed.")
            print("Please install it with one of these commands:")
            print("  pip install llama-cpp-python")
            print("  # For GPU acceleration (if you have CUDA):")
            print("  CMAKE_ARGS=\"-DLLAMA_CUBLAS=on\" pip install llama-cpp-python")
            print("  # For Apple Silicon (if you have Metal):")
            print("  CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python")
            print("  # For AMD GPU:")
            print("  CMAKE_ARGS=\"-DLLAMA_HIPBLAS=on\" pip install llama-cpp-python")
            sys.exit(1)

        print(f"Loading model from {self.model_path}...")
        print(f"Config: Context={self.context_size}, Threads={self.threads}, GPU layers={self.gpu_layers}")
        try:
            self.model = self.Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_threads=self.threads,
                n_gpu_layers=self.gpu_layers,
                verbose=False
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)

    def run_prompt(self, prompt, max_tokens=512):
        """Run a single prompt and return the response"""
        response = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=self.temperature,
            stop=["\n\n", "User:", "Assistant:", "</s>"],
            echo=False
        )
        return response['choices'][0]['text'].strip()

    def run_interactive(self, max_tokens=512):
        """Run in interactive chat mode"""
        print("\nqwen3VL-Local-CLI Interactive Mode")
        print("Type 'quit' or 'exit' to exit")
        print("Type 'help' for commands")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("  quit/exit/q - Exit the program")
                    print("  help - Show this help")
                    print("  reset - Reset conversation history")
                    print("  clear - Clear screen")
                    continue
                elif user_input.lower() == 'reset':
                    self.chat_history = []
                    print("Conversation history reset.")
                    continue
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not user_input:
                    continue
                
                # Build the full prompt with history
                full_prompt = self._build_prompt(user_input)
                
                print("\nQwen3VL: ", end="", flush=True)
                
                # Generate response with streaming
                response = self.model(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    echo=False,
                    stream=True
                )
                
                full_response = ""
                for chunk in response:
                    text = chunk['choices'][0]['text']
                    print(text, end="", flush=True)
                    full_response += text
                    if text in ['\n\n', '</s>']:
                        break
                
                print()  # New line after response
                
                # Update chat history
                self.chat_history.append({"role": "user", "content": user_input})
                self.chat_history.append({"role": "assistant", "content": full_response})
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
    
    def _build_prompt(self, user_input):
        """Build the full prompt with chat history"""
        # For now, using a simple format - this can be enhanced based on the model's expected format
        prompt = "You are Qwen3VL, a helpful AI assistant. Please respond to the following query.\n\n"
        
        for msg in self.chat_history[-4:]:  # Use last 4 exchanges to keep context manageable
            role = msg["role"].capitalize()
            content = msg["content"]
            prompt += f"{role}: {content}\n"
        
        prompt += f"User: {user_input}\nAssistant:"
        return prompt

if __name__ == "__main__":
    main()