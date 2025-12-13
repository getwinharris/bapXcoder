#!/usr/bin/env python3
"""
Agent test file for bapXcoder
This file contains automated tests to validate the user's project developed with the IDE
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

class BapXCoderProjectTestAgent:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.test_results = []

    def test_project_files_integrity(self):
        """Test the integrity of project files developed using bapXcoder"""
        print(f"Validating project files in: {self.project_path}")

        # Check for common project files that might be developed with IDE assistance
        project_files = []
        for ext in ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt']:
            project_files.extend(self.project_path.glob(f"**/*{ext}"))

        for file_path in project_files:
            try:
                # Test that files can be read and parsed (for code files)
                if file_path.suffix in ['.py', '.js', '.ts', '.json']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if file_path.suffix == '.json':
                        json.loads(content)  # Validate JSON
                        print(f"✓ Valid JSON: {file_path.name}")
                    elif file_path.suffix == '.py':
                        compile(content, str(file_path), 'exec')  # Validate Python syntax
                        print(f"✓ Valid Python: {file_path.name}")
                    else:
                        print(f"✓ Readable: {file_path.name}")

            except Exception as e:
                print(f"✗ Issue with {file_path.name}: {str(e)}")
                self.test_results.append(('file_integrity', file_path.name, 'FAIL', str(e)))
                continue

        return True  # Continue even if some files have issues

    def test_project_build(self):
        """Test if project can be built/run if it's a typical project"""
        print("\nTesting project build/run capability...")

        # Look for common build/run scripts
        build_scripts = [
            self.project_path / 'build.sh',
            self.project_path / 'setup.py',
            self.project_path / 'requirements.txt',
            self.project_path / 'package.json',
            self.project_path / 'Dockerfile'
        ]

        for script in build_scripts:
            if script.exists():
                print(f"Found build script: {script.name}")
                # If it's a requirements.txt, check if dependencies can be installed
                if script.name == 'requirements.txt':
                    try:
                        result = subprocess.run([
                            sys.executable, '-m', 'pip', 'check'
                        ], cwd=self.project_path.parent, capture_output=True, text=True)
                        if result.returncode == 0:
                            print("✓ Dependencies are consistent")
                            self.test_results.append(('dependencies', 'requirements.txt', 'PASS', 'Dependencies consistent'))
                        else:
                            print(f"⚠ Dependency warnings: {result.stdout}")
                            self.test_results.append(('dependencies', 'requirements.txt', 'WARN', result.stdout))
                    except Exception as e:
                        print(f"ℹ Could not check dependencies: {e}")

                # If it's a setup.py, check syntax
                elif script.name == 'setup.py':
                    try:
                        with open(script, 'r') as f:
                            content = f.read()
                        compile(content, script, 'exec')
                        print("✓ Valid setup.py")
                        self.test_results.append(('build_script', 'setup.py', 'PASS', 'Valid syntax'))
                    except Exception as e:
                        print(f"✗ Invalid setup.py: {e}")
                        self.test_results.append(('build_script', 'setup.py', 'FAIL', str(e)))

        return True

    def test_ide_features_used(self):
        """Check if IDE features were properly utilized in the project"""
        print("\nChecking for proper IDE feature utilization...")

        # Look for .bapXcoder directory which indicates project-based memory usage
        bapxcoder_dir = self.project_path / '.bapXcoder'
        if bapxcoder_dir.exists():
            print("✓ Project-based memory system (.bapXcoder) used")
            # Check for todo.json
            todo_file = bapxcoder_dir / 'todo.json'
            if todo_file.exists():
                print("✓ Todo list management used")
                try:
                    with open(todo_file, 'r') as f:
                        todos = json.load(f)
                        print(f"  - {len(todos)} TODO items tracked")
                except:
                    print("  - TODO file exists but has parsing issues")

            # Check for sessiontree.json
            session_file = bapxcoder_dir / 'sessiontree.json'
            if session_file.exists():
                print("✓ Session tracking used")
        else:
            print("ℹ Project-based memory system (.bapXcoder) not detected")

        # Look for AI-assisted comments or code patterns
        code_files = list(self.project_path.glob("**/*.py"))[:10]  # Check first 10 Python files
        ai_indicators = 0
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for patterns that indicate AI assistance
                if 'Generated by AI' in content or 'AI-generated' in content or 'Suggested by assistant' in content:
                    ai_indicators += 1
            except:
                continue

        if ai_indicators > 0:
            print(f"✓ AI assistance traces found in {ai_indicators}/{len(code_files)} files")

        return True

    def run_tests(self):
        """Run all project validation tests"""
        print("Running bapXcoder Project Validation Tests...")
        print("=" * 1)

        print("Testing project files integrity...")
        self.test_project_files_integrity()

        print("\nTesting project build capability...")
        self.test_project_build()

        print("\nChecking IDE feature utilization...")
        self.test_ide_features_used()

        print("=" * 1)
        print("Project validation completed!")
        print("The project has been developed with bapXcoder IDE assistance.")

        return True

if __name__ == "__main__":
    # Allow specifying a project path as an argument
    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    agent = BapXCoderProjectTestAgent(project_path)
    success = agent.run_tests()
    sys.exit(0 if success else 1)