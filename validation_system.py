#!/usr/bin/env python3
"""
AI-driven testing and validation system for bapXcoder
Implements automated testing that validates code after each change
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class AIValidationSystem:
    """AI-driven validation system for bapXcoder projects"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.test_log_file = project_path / ".bapXcoder" / "validation_log.json"
        self.setup_validation_directory()

    def setup_validation_directory(self):
        """
        Set up the validation infrastructure

        Function: Creates validation directory and initializes log files
        Connection: Links to project-based memory system in .bapXcoder directory
        Purpose: Establish AI-driven testing framework within projects
        Internal wiring: Connects to validation logging and result aggregation systems
        """
        bapxcoder_dir = self.project_path / ".bapXcoder"
        bapxcoder_dir.mkdir(exist_ok=True)

        # Initialize validation log if it doesn't exist
        if not self.test_log_file.exists():
            with open(self.test_log_file, 'w') as f:
                json.dump({
                    'validation_history': [],
                    'last_tested_files': [],
                    'overall_success_rate': 0,
                    'test_stats': {
                        'total_runs': 0,
                        'successful_runs': 0,
                        'failed_runs': 0
                    }
                }, f, indent=2)

    def run_syntax_validation(self, file_path: str) -> Tuple[bool, str]:
        """Run syntax validation on a code file"""
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.py':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                return True, "Python syntax validation passed"
            except SyntaxError as e:
                return False, f"Python syntax error: line {e.lineno}, {str(e.msg)}"
            except Exception as e:
                return False, f"Python validation error: {str(e)}"

        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            try:
                result = subprocess.run([
                    'node', '-c', file_path
                ], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return True, "JavaScript/TypeScript syntax validation passed"
                else:
                    return False, f"JS/TS syntax error: {result.stderr[:100]}..."  # Limit size
            except subprocess.TimeoutExpired:
                return False, "JavaScript validation timed out"
            except FileNotFoundError:
                # Node.js not found, try basic read validation
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                    return True, "JS/TS file is readable (no Node.js available for syntax check)"
                except Exception as e:
                    return False, f"JS/TS file read error: {str(e)}"
            except Exception as e:
                return False, f"JS/TS validation error: {str(e)}"

        elif file_ext == '.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return True, "JSON validation passed"
            except Exception as e:
                return False, f"JSON syntax error: {str(e)}"

        else:
            # For other files, just check readability
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.read()
                return True, "File readable"
            except Exception as e:
                return False, f"File read error: {str(e)}"

    def run_unit_tests(self, file_path: str) -> Tuple[bool, str, List[str]]:
        """Run unit tests related to a changed file"""
        file_ext = Path(file_path).suffix.lower()
        results = []

        if file_ext == '.py':
            # Look for test files in the same directory or test directory
            test_dir = Path(file_path).parent / "test"
            test_file = Path(file_path).parent / f"test_{Path(file_path).stem}.py"
            test_alt_file = Path(file_path).parent / f"{Path(file_path).stem}_test.py"

            test_candidates = [test_file, test_alt_file]
            if test_dir.exists():
                test_candidates.extend(test_dir.glob(f"**/test_{Path(file_path).stem}.py"))
                test_candidates.extend(test_dir.glob(f"**/*_test.py"))

            for test_candidate in test_candidates:
                if test_candidate.exists():
                    try:
                        result = subprocess.run([
                            sys.executable, '-m', 'pytest', str(test_candidate)
                        ], capture_output=True, text=True, timeout=60)

                        if result.returncode == 0:
                            results.append(f"Unit tests in {test_candidate.name}: PASSED")
                        else:
                            return False, f"Unit tests in {test_candidate.name}: FAILED", [f"Test output: {result.stdout}", f"Errors: {result.stderr}"]
                    except Exception as e:
                        results.append(f"Error running tests in {test_candidate.name}: {str(e)}")

            if not results:
                results.append("No related test files found")

        return True, "Unit tests completed", results

    def run_functional_tests(self, project_dir: str) -> Tuple[bool, str, List[str]]:
        """Run functional/integration tests for the project"""
        results = []

        # Look for common test runners and test files
        test_patterns = [
            f"{project_dir}/test_*.py",
            f"{project_dir}/*_test.py",
            f"{project_dir}/test/**/*.py",
            f"{project_dir}/test/**/*.js",
            f"{project_dir}/**/*spec.js",
            f"{project_dir}/**/*test.js",
        ]

        success = True
        for pattern in test_patterns:
            test_files = Path(pattern).parent.glob(pattern.split('/')[-1])
            for test_file in test_files:
                try:
                    if test_file.suffix == '.py':
                        result = subprocess.run([
                            sys.executable, '-m', 'unittest', str(test_file)
                        ], capture_output=True, text=True, timeout=30)

                        if result.returncode == 0:
                            results.append(f"Functional test {test_file.name}: PASSED")
                        else:
                            results.append(f"Functional test {test_file.name}: FAILED")
                            success = False
                    elif test_file.suffix in ['.js', '.ts']:
                        # For now, just check syntax validity of test files
                        result = subprocess.run([
                            'node', '-c', str(test_file)
                        ], capture_output=True, text=True, timeout=10)

                        if result.returncode == 0:
                            results.append(f"Functional test syntax {test_file.name}: PASSED")
                        else:
                            results.append(f"Functional test syntax {test_file.name}: FAILED - {result.stderr}")
                            success = False
                except Exception as e:
                    results.append(f"Error running test {test_file.name}: {str(e)}")

        if not results:
            results.append("No functional test files found")

        return success, "Functional tests completed", results

    def validate_file_change(self, file_path: str) -> Dict:
        """Validate a single file after it's been changed"""
        timestamp = time.time()

        print(f"Validating file change: {file_path}")

        # Run syntax validation
        syntax_ok, syntax_msg = self.run_syntax_validation(file_path)

        # Log the validation
        validation_result = {
            'timestamp': timestamp,
            'file_path': file_path,
            'syntax_valid': syntax_ok,
            'syntax_message': syntax_msg,
            'unit_test_results': [],
            'overall_success': syntax_ok
        }

        # If syntax is OK, run unit tests if appropriate
        if syntax_ok:
            unit_ok, unit_msg, unit_details = self.run_unit_tests(file_path)
            validation_result['unit_test_success'] = unit_ok
            validation_result['unit_test_message'] = unit_msg
            validation_result['unit_test_details'] = unit_details
            validation_result['overall_success'] = unit_ok

            # Run functional tests for the entire project
            func_ok, func_msg, func_details = self.run_functional_tests(str(Path(file_path).parent))
            validation_result['functional_test_success'] = func_ok
            validation_result['functional_test_message'] = func_msg
            validation_result['functional_test_details'] = func_details
            validation_result['overall_success'] = validation_result['overall_success'] and func_ok

        # Update validation log
        self.update_validation_log(validation_result)

        return validation_result

    def update_validation_log(self, result: Dict):
        """Update the validation log with a new result"""
        try:
            with open(self.test_log_file, 'r') as f:
                log_data = json.load(f)
        except:
            log_data = {
                'validation_history': [],
                'last_tested_files': [],
                'overall_success_rate': 0,
                'test_stats': {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'failed_runs': 0
                }
            }

        log_data['validation_history'].append(result)
        log_data['last_tested_files'].append(result['file_path'])

        # Update statistics
        log_data['test_stats']['total_runs'] += 1
        if result['overall_success']:
            log_data['test_stats']['successful_runs'] += 1
        else:
            log_data['test_stats']['failed_runs'] += 1

        log_data['overall_success_rate'] = log_data['test_stats']['successful_runs'] / max(1, log_data['test_stats']['total_runs'])

        # Keep only the last 100 validation records to avoid log growing too large
        if len(log_data['validation_history']) > 100:
            log_data['validation_history'] = log_data['validation_history'][-100:]

        # Keep only the last 20 tested files
        if len(log_data['last_tested_files']) > 20:
            log_data['last_tested_files'] = log_data['last_tested_files'][-20:]

        with open(self.test_log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def get_validation_summary(self) -> Dict:
        """Get a summary of validation results"""
        try:
            with open(self.test_log_file, 'r') as f:
                log_data = json.load(f)

            return {
                'success_rate': log_data.get('overall_success_rate', 0),
                'total_validations': log_data['test_stats']['total_runs'],
                'successful_validations': log_data['test_stats']['successful_runs'],
                'failed_validations': log_data['test_stats']['failed_runs'],
                'recent_validations': log_data['validation_history'][-5:],  # Last 5 validations
                'last_tested_files': log_data['last_tested_files'][-5:]    # Last 5 tested files
            }
        except:
            return {
                'success_rate': 0,
                'total_validations': 0,
                'successful_validations': 0,
                'failed_validations': 0,
                'recent_validations': [],
                'last_tested_files': []
            }


class AITestRunner:
    """AI-powered test runner that validates code and suggests fixes"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.validation_system = AIValidationSystem(project_path)
        self.test_results = {}

    def validate_project_stage(self, stage_description: str = "", changed_files: List[str] = []) -> Dict:
        """Validate project at a particular development stage"""
        results = {
            'stage': stage_description,
            'timestamp': time.time(),
            'file_validations': [],
            'project_overall_status': True,
            'suggestions': []
        }

        if not changed_files:
            # If no specific files provided, validate recently changed files
            for file_path in self.project_path.glob("**/*.py"):
                if file_path.name != '__pycache__':
                    changed_files.append(str(file_path))

        for file_path in changed_files:
            validation_result = self.validation_system.validate_file_change(file_path)
            results['file_validations'].append(validation_result)

            if not validation_result['overall_success']:
                results['project_overall_status'] = False

        # Generate AI suggestions based on validation results
        if not results['project_overall_status']:
            suggestions = self.generate_fix_suggestions(results['file_validations'])
            results['suggestions'] = suggestions

        return results

    def run_individual_file_tests(self, file_path: str) -> Dict:
        """Run comprehensive tests for an individual file and return results"""
        validation_result = self.validation_system.validate_file_change(file_path)

        # Run additional tests
        performance_results = self.run_performance_tests(file_path)

        # Combine all analysis
        ai_analysis = self.analyze_file_quality(file_path)
        ai_analysis['performance_metrics'] = performance_results['metrics']
        if performance_results['performance_issues']:
            ai_analysis['performance_issues'] = performance_results['performance_issues']
            ai_analysis['suggestions'].extend([f"Performance: {issue}" for issue in performance_results['performance_issues']])

        # Generate AI fix suggestions
        all_issues = []
        if 'security_issues' in ai_analysis and ai_analysis['security_issues']:
            all_issues.extend(ai_analysis['security_issues'])
        if 'performance_issues' in ai_analysis and ai_analysis['performance_issues']:
            all_issues.extend(ai_analysis['performance_issues'])

        fix_suggestions = self.generate_ai_fix_suggestions(file_path, all_issues)
        ai_analysis['fix_suggestions'] = fix_suggestions

        test_result = {
            'file_path': file_path,
            'validation_result': validation_result,
            'ai_analysis': ai_analysis,
            'timestamp': time.time(),
            'test_summary': {
                'syntax_valid': validation_result['syntax_valid'],
                'security_issues_count': len(ai_analysis.get('security_issues', [])),
                'performance_issues_count': len(ai_analysis.get('performance_issues', [])),
                'suggestions_count': len(ai_analysis.get('suggestions', [])),
                'fix_suggestions_count': len(ai_analysis.get('fix_suggestions', []))
            }
        }

        # Store result for later reference
        self.test_results[file_path] = test_result

        return test_result

    def analyze_file_quality(self, file_path: str) -> Dict:
        """AI analysis of file quality and potential improvements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_ext = Path(file_path).suffix.lower()
            analysis = {
                'code_complexity': self.assess_complexity(content),
                'security_issues': self.scan_security(content, file_ext),
                'performance_issues': self.scan_performance(content, file_ext),
                'best_practices': self.check_best_practices(content, file_ext),
                'suggestions': []
            }

            # Generate AI-powered suggestions based on analysis
            if analysis['security_issues']:
                analysis['suggestions'].append("Security concerns detected - review the code for potential vulnerabilities")

            if analysis['performance_issues']:
                analysis['suggestions'].append("Performance issues detected - consider optimization")

            if analysis['best_practices']:
                analysis['suggestions'].extend(analysis['best_practices'])

            return analysis
        except Exception as e:
            return {
                'error': f"Could not analyze {file_path}: {str(e)}",
                'code_complexity': 0,
                'security_issues': [],
                'performance_issues': [],
                'best_practices': [],
                'suggestions': []
            }

    def assess_complexity(self, code: str) -> int:
        """Assess code complexity on a scale of 1-10"""
        complexity_score = 5  # Default medium complexity

        # Count functions and classes
        function_count = code.count('def ')
        class_count = code.count('class ')

        # Count nested structures
        nested_score = code.count('    def ') + code.count('\tif ') + code.count('\tfor ') + code.count('\twhile ')

        # Increase complexity based on counts
        complexity_score += min(function_count, 5) + min(class_count, 3) + min(nested_score/10, 3)

        return min(int(complexity_score), 10)

    def scan_security(self, code: str, ext: str) -> List[str]:
        """Scan for basic security issues in code"""
        issues = []

        if ext == '.py':
            if 'eval(' in code:
                issues.append("Use of eval() poses security risks")
            if 'exec(' in code:
                issues.append("Use of exec() poses security risks")
            if 'os.system(' in code or 'subprocess.' in code:
                issues.append("External command execution found - validate inputs carefully")
            if 'password' in code.lower() and '=' in code:
                issues.append("Potential hardcoded credentials found")
            if 'input(' in code and ('sql' in code.lower() or 'query' in code.lower()):
                issues.append("Potential SQL injection risk - validate database inputs carefully")
            if "'SELECT" in code or '"SELECT' in code:
                issues.append("Direct SQL query found - consider using parameterized queries")

        return issues

    def run_integration_tests(self, project_path: str) -> Dict:
        """Run integration tests for the project"""
        results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }

        # Look for integration test files
        integration_test_patterns = [
            f"{project_path}/**/*integration*test*.py",
            f"{project_path}/**/*integration_test*.py",
            f"{project_path}/**/*test_integration*.py",
            f"{project_path}/integration_tests/*.py",
            f"{project_path}/tests/integration/*.py"
        ]

        for pattern in integration_test_patterns:
            try:
                import glob
                test_files = glob.glob(pattern, recursive=True)
                for test_file in test_files:
                    try:
                        result = subprocess.run([
                            sys.executable, '-m', 'pytest', test_file, '-v'
                        ], capture_output=True, text=True, timeout=120)

                        results['tests_run'] += 1
                        if result.returncode == 0:
                            results['tests_passed'] += 1
                            results['details'].append(f"Integration test passed: {test_file}")
                        else:
                            results['tests_failed'] += 1
                            results['details'].append(f"Integration test failed: {test_file} - {result.stderr[:100]}")
                    except subprocess.TimeoutExpired:
                        results['tests_failed'] += 1
                        results['details'].append(f"Integration test timed out: {test_file}")
                    except Exception as e:
                        results['details'].append(f"Error running integration test {test_file}: {str(e)}")
            except Exception:
                continue  # If one pattern fails, try others

        return results

    def run_performance_tests(self, file_path: str) -> Dict:
        """Run basic performance tests on the file"""
        results = {
            'performance_issues': [],
            'metrics': {}
        }

        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Analyze for performance issues
            lines = content.split('\n')
            results['metrics']['line_count'] = len(lines)
            results['metrics']['file_size'] = len(content)

            # Check for inefficient patterns
            for i, line in enumerate(lines, 1):
                if 'for ' in line and ' in range(' in line:
                    # Check for potentially large ranges
                    import re
                    matches = re.findall(r'range\((\d+)\)', line)
                    for match in matches:
                        if int(match) > 100000:  # Large iteration
                            results['performance_issues'].append(f"Line {i}: Large loop range detected ({match} iterations)")

                if 'import ' in line and i < 10:  # Check if imports are in module scope
                    results['metrics'].setdefault('imports_count', 0)
                    results['metrics']['imports_count'] += 1

            # Check for potential memory issues
            if 'while True:' in content:
                results['performance_issues'].append("Infinite loop detected - potential memory/CPU issue")

            if content.count('append(') > 100:
                results['performance_issues'].append("Many list append operations - consider using more efficient data structures")

        except Exception as e:
            results['performance_issues'].append(f"Error analyzing performance: {str(e)}")

        return results

    def generate_ai_fix_suggestions(self, file_path: str, issues: List[str]) -> List[str]:
        """Generate AI-powered fix suggestions for identified issues"""
        suggestions = []

        # Categorize issues and provide specific suggestions
        for issue in issues:
            if "security" in issue.lower() or "eval" in issue or "exec" in issue:
                suggestions.append("RECOMMENDATION: Replace eval/exec with safer alternatives like ast.literal_eval() for data parsing")
            elif "password" in issue.lower():
                suggestions.append("RECOMMENDATION: Store credentials in environment variables or secure configuration files")
            elif "large loop" in issue.lower():
                suggestions.append("RECOMMENDATION: Consider using generators or breaking the loop into smaller chunks")
            elif "SQL injection" in issue:
                suggestions.append("RECOMMENDATION: Use parameterized queries or an ORM to prevent SQL injection")

        # Add general suggestions based on file type
        ext = Path(file_path).suffix.lower()
        if ext == '.py':
            suggestions.extend([
                "Consider adding type hints for better code maintenance",
                "Add comprehensive unit tests for all functions"
            ])

        return suggestions

    def run_project_wide_tests(self) -> Dict:
        """Run comprehensive tests across the entire project"""
        results = {
            'files_analyzed': 0,
            'total_issues': 0,
            'security_issues': 0,
            'performance_issues': 0,
            'suggestions': [],
            'file_reports': [],
            'summary': {}
        }

        # Walk through all files in the project
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json']:
                try:
                    file_analysis = self.analyze_file_quality(str(file_path))
                    results['files_analyzed'] += 1

                    # Collect issues
                    security_count = len(file_analysis.get('security_issues', []))
                    perf_count = len(file_analysis.get('performance_issues', []))

                    results['security_issues'] += security_count
                    results['performance_issues'] += perf_count
                    results['total_issues'] += security_count + perf_count
                    results['suggestions'].extend(file_analysis.get('suggestions', []))

                    # Store file-specific report
                    file_report = {
                        'file_path': str(file_path),
                        'security_issues': file_analysis.get('security_issues', []),
                        'performance_issues': file_analysis.get('performance_issues', []),
                        'complexity': file_analysis.get('code_complexity', 0),
                        'suggestions': file_analysis.get('suggestions', [])
                    }
                    results['file_reports'].append(file_report)

                except Exception as e:
                    print(f"Error analyzing {file_path}: {str(e)}")
                    continue

        # Generate project summary
        results['summary'] = {
            'total_files_scanned': results['files_analyzed'],
            'total_issues_found': results['total_issues'],
            'security_issues_found': results['security_issues'],
            'performance_issues_found': results['performance_issues'],
            'suggestions_available': len(results['suggestions']),
            'overall_risk_assessment': self.calculate_risk_level(results)
        }

        return results

    def calculate_risk_level(self, results: Dict) -> str:
        """Calculate overall risk level based on test results"""
        total_files = results['files_analyzed']
        if total_files == 0:
            return "unknown"

        issue_density = results['total_issues'] / total_files

        if issue_density > 2.0:
            return "high"
        elif issue_density > 1.0:
            return "medium"
        elif issue_density > 0.0:
            return "low"
        else:
            return "none"

    def scan_performance(self, code: str, ext: str) -> List[str]:
        """Scan for basic performance issues in code"""
        issues = []

        if ext == '.py':
            if 'for ' in code and 'in range(' in code and 'range(10000' in code:
                issues.append("Large loop detected - consider optimization")
            if code.count('import ') > 10:
                issues.append("Too many imports at module level - consider lazy imports")

        return issues

    def generate_fix_suggestions(self, validation_results: List[Dict]) -> List[str]:
        """Generate AI-powered suggestions for fixing validation issues"""
        suggestions = []

        for result in validation_results:
            if not result['overall_success']:
                if not result['syntax_valid']:
                    suggestions.append(f"Fix syntax error in {result['file_path']}: {result['syntax_message']}")
                else:
                    if result.get('unit_test_success') == False:
                        suggestions.append(f"Address unit test failures in {result['file_path']}")
                    if result.get('functional_test_success', True) == False:
                        suggestions.append(f"Address functional test failures in {result['file_path']}")

        return suggestions

    def auto_test_after_changes(self, file_path: str) -> Dict:
        """Automatically test file after changes"""
        validation_result = self.validation_system.validate_file_change(file_path)

        # Log result to session tree
        try:
            session_tree_file = self.project_path / ".bapXcoder" / "sessiontree.json"
            if session_tree_file.exists():
                with open(session_tree_file, 'r') as f:
                    session_data = json.load(f)

                # Update session with latest validation
                if 'validation_results' not in session_data:
                    session_data['validation_results'] = []

                session_data['validation_results'].append({
                    'file': file_path,
                    'timestamp': validation_result['timestamp'],
                    'success': validation_result['overall_success'],
                    'issues': []
                })

                # Add specific issues if validation failed
                if not validation_result['overall_success']:
                    if not validation_result.get('syntax_valid', True):
                        session_data['validation_results'][-1]['issues'].append({
                            'type': 'syntax',
                            'message': validation_result['syntax_message']
                        })
                    if not validation_result.get('unit_test_success', True):
                        session_data['validation_results'][-1]['issues'].append({
                            'type': 'unit_test',
                            'message': validation_result['unit_test_message']
                        })

                with open(session_tree_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not update session tree with validation results: {e}")

        return validation_result


# Global validation system instance (initialized per project)
ai_validator = None


def initialize_ai_testing(project_path: str) -> bool:
    """Initialize the AI testing system for a project"""
    global ai_validator
    try:
        ai_validator = AITestRunner(Path(project_path))
        print(f"AI validation system initialized for project: {project_path}")
        return True
    except Exception as e:
        print(f"Could not initialize AI validation system: {e}")
        return False


def validate_file_on_change(file_path: str) -> Optional[Dict]:
    """Validate a file after it has been changed"""
    global ai_validator
    if ai_validator:
        try:
            result = ai_validator.auto_test_after_changes(file_path)
            return result
        except Exception as e:
            print(f"Error validating file {file_path}: {e}")
            return None
    else:
        print("AI validation system not initialized - please set project first")
        return None


def get_project_validation_summary() -> Optional[Dict]:
    """Get validation summary for the current project"""
    global ai_validator
    if ai_validator:
        try:
            return ai_validator.validation_system.get_validation_summary()
        except Exception as e:
            print(f"Error getting validation summary: {e}")
            return None
    else:
        print("AI validation system not initialized - please set project first")
        return None


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        initialize_ai_testing(project_path)

        if len(sys.argv) > 2:
            file_path = sys.argv[2]
            result = validate_file_on_change(file_path)
            if result:
                print(f"Validation result: {result}")
            else:
                print("Validation failed")
    else:
        print("Usage: python validation_system.py <project_path> [file_path_to_validate]")