"""
Syntax Checker Module for bapXcoder
Provides live syntax checking and validation without relying on LSP
"""

import subprocess
import sys
import threading
import time
from pathlib import Path
import json

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    class FileSystemEventHandler:
        pass
    Observer = None

class LiveSyntaxChecker:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.syntax_errors = {}
        self.observer = Observer()
        self.watcher = None
        self.running = False
    
    def get_syntax_checker(self, file_path):
        """Get appropriate syntax checker for file type"""
        ext = Path(file_path).suffix.lower()

        if ext == '.py':
            return self.check_python_syntax
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            return self.check_javascript_syntax
        elif ext == '.html':
            return self.check_html_syntax
        elif ext == '.css':
            return self.check_css_syntax
        elif ext == '.json':
            return self.check_json_syntax
        else:
            return self.check_generic_text_syntax
    
    def check_python_syntax(self, file_path):
        """Check Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')  # Test for syntax errors
            return True, []
        except SyntaxError as e:
            return False, [{
                'line': e.lineno or 0,
                'column': e.offset or 0,
                'message': str(e.msg or 'Syntax error'),
                'severity': 'error'
            }]
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'Syntax check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_javascript_syntax(self, file_path):
        """Check JavaScript/TypeScript syntax using Node.js"""
        try:
            result = subprocess.run([
                'node', '-c', str(file_path)
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return True, []
            else:
                # Parse error output
                errors = []
                for line in result.stderr.split('\n'):
                    if ': line' in line and ': column' in line:
                        # Basic parsing of Node.js error format
                        errors.append({
                            'line': 0,  # Would need more complex parsing
                            'column': 0,
                            'message': line.strip(),
                            'severity': 'error'
                        })
                return False, errors
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'JavaScript syntax check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_html_syntax(self, file_path):
        """Basic HTML syntax check"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple validation for unclosed tags
            errors = []
            # This is a basic implementation - a full one would use a proper HTML parser
            if '<script>' in content and '</script>' not in content:
                errors.append({
                    'line': 0,
                    'column': 0,
                    'message': 'Unclosed <script> tag detected',
                    'severity': 'warning'
                })
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'HTML syntax check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_css_syntax(self, file_path):
        """Basic CSS syntax check"""
        try:
            import cssutils
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parser = cssutils.CSSParser()
            sheet = parser.parseString(content)
            
            return True, []
        except ImportError:
            # cssutils not available, use basic validation
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            errors = []
            if '{' in content and '}' not in content:
                errors.append({
                    'line': 0,
                    'column': 0,
                    'message': 'CSS appears to have unclosed block(s)',
                    'severity': 'warning'
                })
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'CSS syntax check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_json_syntax(self, file_path):
        """Check JSON syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)  # Test for valid JSON
            return True, []
        except json.JSONDecodeError as e:
            return False, [{
                'line': e.lineno if hasattr(e, 'lineno') else 0,
                'column': e.colno if hasattr(e, 'colno') else 0,
                'message': str(e.msg) if hasattr(e, 'msg') else str(e),
                'severity': 'error'
            }]
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'JSON syntax check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_generic_text_syntax(self, file_path):
        """Generic syntax check for text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return True, []
        except Exception as e:
            return False, [{
                'line': 0,
                'column': 0,
                'message': f'Text file check error: {str(e)}',
                'severity': 'warning'
            }]
    
    def check_file_syntax(self, file_path):
        """Check syntax for a specific file"""
        checker = self.get_syntax_checker(file_path)
        is_valid, errors = checker(file_path)
        
        if not is_valid:
            self.syntax_errors[file_path] = errors
        elif file_path in self.syntax_errors:
            del self.syntax_errors[file_path]
        
        return is_valid, errors
    
    def start_watching(self):
        """Start watching files for changes"""
        self.running = True
        
        # Set up file watcher
        event_handler = SyntaxWatcherHandler(self)
        self.observer.schedule(event_handler, self.project_path, recursive=True)
        self.observer.start()
        
        print(f"Started syntax checking for: {self.project_path}")
        print("Watching files for syntax changes...")
    
    def stop_watching(self):
        """Stop watching files"""
        self.running = False
        self.observer.stop()
        self.observer.join()
        print("Stopped syntax checking.")

class SyntaxWatcherHandler(FileSystemEventHandler):
    def __init__(self, syntax_checker):
        self.syntax_checker = syntax_checker
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in ['.py', '.js', '.ts', '.html', '.css', '.json', '.jsx', '.tsx']:
            # Delay slightly to ensure file write is complete
            time.sleep(0.1)
            is_valid, errors = self.syntax_checker.check_file_syntax(event.src_path)
            
            # In a real implementation, this would emit the errors to the UI
            if errors:
                print(f"Syntax errors found in {event.src_path}:")
                for error in errors:
                    print(f"  Line {error['line']}: {error['message']}")

# Global syntax checker instance
syntax_checker = None

def initialize_syntax_checker(project_path):
    """Initialize the live syntax checker"""
    global syntax_checker
    if WATCHDOG_AVAILABLE:
        syntax_checker = LiveSyntaxChecker(project_path)
        return True
    else:
        print("Installing file watching dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "watchdog"])
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            global WATCHDOG_AVAILABLE
            WATCHDOG_AVAILABLE = True
            syntax_checker = LiveSyntaxChecker(project_path)
            return True
        except ImportError:
            print("Could not initialize syntax checker - install 'watchdog' manually")
            return False

def get_syntax_errors(file_path):
    """Get syntax errors for a file"""
    global syntax_checker
    if syntax_checker:
        is_valid, errors = syntax_checker.check_file_syntax(file_path)
        return errors
    return []

def start_syntax_monitoring(project_path):
    """Start the syntax monitoring service"""
    global syntax_checker
    if not syntax_checker:
        initialize_syntax_checker(project_path)
    
    if syntax_checker:
        syntax_checker.start_watching()
        return True
    return False

def stop_syntax_monitoring():
    """Stop the syntax monitoring service"""
    global syntax_checker
    if syntax_checker:
        syntax_checker.stop_watching()