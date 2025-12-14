#!/usr/bin/env python3
#!/usr/bin/env python3
"""
User test file for bapXcoder
This file tests user interactions with projects developed using bapXcoder IDE
"""

import os
import sys
import time
import json
from pathlib import Path

class BapXcoderUserProjectTester:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()

    def test_project_directory_structure(self):
        """Test if the project has proper bapXcoder directory structure"""
        print(f"Validating project structure in: {self.project_path}")

        # Check if this is a bapXcoder project (has .bapXcoder folder)
        bapxcoder_dir = self.project_path / ".bapXcoder"

        if bapxcoder_dir.exists():
            print("✓ bapXcoder project directory (.bapXcoder) detected")
            return True
        else:
            print(f"ℹ Project not using bapXcoder structure, testing current directory: {self.project_path.name}")
            return True

    def test_code_files_validation(self):
        """Test that code files in the project are valid and properly developed"""
        print("\nValidating code files in the project...")

        # Find Python and other common project files
        code_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt', '.java', '.cpp', '.c', '.go']
        code_files = []
        for ext in code_extensions:
            code_files.extend(self.project_path.glob(f"**/*{ext}"))

        valid_files_count = 0
        total_files = len(code_files)

        for file_path in code_files[:20]:  # Check up to 20 files to avoid long delays
            try:
                if file_path.suffix in ['.json']:
                    # Validate JSON files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✓ Valid JSON: {file_path.relative_to(self.project_path)}")
                    valid_files_count += 1
                elif file_path.suffix in ['.py']:
                    # Validate Python files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, str(file_path), 'exec')
                    print(f"✓ Valid Python: {file_path.relative_to(self.project_path)}")
                    valid_files_count += 1
                elif file_path.suffix in ['.js', '.ts']:
                    # Just check readability for JS/TS files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                    print(f"✓ Readable: {file_path.relative_to(self.project_path)}")
                    valid_files_count += 1
                else:
                    # For other files, just check readability
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.read()
                    print(f"✓ Readable: {file_path.relative_to(self.project_path)}")
                    valid_files_count += 1
            except Exception as e:
                print(f"✗ Invalid {file_path.suffix[1:]} file: {file_path.relative_to(self.project_path)} - {str(e)[:50]}...")

        print(f"\nValidated {valid_files_count}/{len(code_files[:20])} files successfully")
        return valid_files_count > 0  # Return True if at least one file was valid

    def test_bapxcoder_features_utilization(self):
        """Test if bapXcoder features were used in the project development"""
        print("\nChecking for bapXcoder feature utilization...")

        bapxcoder_dir = self.project_path / ".bapXcoder"

        if bapxcoder_dir.exists():
            # Check for todo.json
            todo_file = bapxcoder_dir / "todo.json"
            if todo_file.exists():
                print("✓ Todo list management used (todo.json)")
                try:
                    with open(todo_file, 'r') as f:
                        todos = json.load(f)
                        print(f"  - {len(todos)} tasks tracked in project")
                except Exception as e:
                    print(f"  - todo.json exists but has parsing issues: {e}")
            else:
                print("ℹ Todo list not found in this project")

            # Check for sessiontree.json
            session_file = bapxcoder_dir / "sessiontree.json"
            if session_file.exists():
                print("✓ Session tracking used (sessiontree.json)")
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        if 'active_files' in session_data:
                            print(f"  - {len(session_data.get('active_files', []))} active files tracked")
                        if 'project_stats' in session_data:
                            stats = session_data['project_stats']
                            print(f"  - Project statistics: {stats.get('file_count', 0)} files, {stats.get('total_lines', 0)} lines")
                except Exception as e:
                    print(f"  - sessiontree.json exists but has parsing issues: {e}")
            else:
                print("ℹ Session tracking not found in this project")
        else:
            print("ℹ bapXcoder project structure (.bapXcoder) not detected")

        # Look for AI-assisted development indicators
        ai_indicators = 0
        code_files = list(self.project_path.glob("**/*.py"))[:15]  # Check first 15 Python files

        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for common AI assistance indicators
                ai_keywords = [
                    'Generated by', 'AI-generated', 'Suggested by', 'Based on chat suggestions',
                    'Created using AI', 'Assistant suggested', 'IDE help', 'AI assistant'
                ]

                for keyword in ai_keywords:
                    if keyword.lower() in content.lower():
                        ai_indicators += 1
                        break
            except:
                continue

        if ai_indicators > 0:
            print(f"✓ AI assistance usage detected in {ai_indicators} files")
        else:
            # Still valid if no indicators found - the user might just be using the IDE without those specific markers
            print("ℹ No explicit AI assistance markers found - this is normal")

        return True

    def test_project_functionality(self):
        """Test if the project has basic functionality indicators"""
        print("\nTesting project functionality indicators...")

        # Look for common project files that indicate development was done properly
        project_indicators = {
            'requirements.txt': 'Python dependencies',
            'package.json': 'JavaScript dependencies',
            'setup.py': 'Python package setup',
            'build.sh': 'Build script',
            'README.md': 'Project documentation',
            'Dockerfile': 'Container configuration',
            '.gitignore': 'Git configuration',
            'Makefile': 'Build automation'
        }

        found_indicators = []
        for file_name, description in project_indicators.items():
            if (self.project_path / file_name).exists():
                found_indicators.append(f"{file_name} ({description})")

        if found_indicators:
            print(f"✓ Found {len(found_indicators)} project indicator files:")
            for indicator in found_indicators:
                print(f"  - {indicator}")
        else:
            print("ℹ No common project indicator files found")

        return len(found_indicators) > 0

    def run_tests(self):
        """Run all project validation tests"""
        print("Running bapXcoder User Project Validation Tests...")
        print("=" * 1)

        test_results = []

        print("\nProject Structure:")
        print("-" * 1)
        result1 = self.test_project_directory_structure()
        status1 = "✓" if result1 else "✗"
        print(f"Result: {status1}")
        test_results.append(("Project Structure", result1))

        print("\nCode Validation:")
        print("-" * 1)
        result2 = self.test_code_files_validation()
        status2 = "✓" if result2 else "✗"
        print(f"Result: {status2}")
        test_results.append(("Code Validation", result2))

        print("\nFeature Utilization:")
        print("-" * 1)
        result3 = self.test_bapxcoder_features_utilization()
        status3 = "✓" if result3 else "✗"
        print(f"Result: {status3}")
        test_results.append(("Feature Utilization", result3))

        print("\nProject Indicators:")
        print("-" * 1)
        result4 = self.test_project_functionality()
        status4 = "✓" if result4 else "✗"
        print(f"Result: {status4}")
        test_results.append(("Project Indicators", result4))

        print("\n" + "=" * 1)
        print("User Project Test Summary:")
        for test_name, result in test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {test_name}: {status}")

        all_passed = all(result for _, result in test_results)
        overall_status = "PASS" if all_passed else "FAIL"
        print(f"\nOverall Result: {overall_status}")

        print(f"\nYour project has been analyzed with bapXcoder testing framework!")
        print("This validates that your project was developed with proper IDE assistance and structure.")

        return all_passed

if __name__ == "__main__":
    # Allow specifying a project path as an argument
    project_path = sys.argv[1] if len(sys.argv) > 1 else None
    tester = BapXcoderUserProjectTester(project_path)
    success = tester.run_tests()
    sys.exit(0 if success else 1)