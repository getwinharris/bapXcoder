import os
import json
from pathlib import Path
from datetime import datetime

class ProjectExplorer:
    """Handles project file exploration and management for bapXcoder"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.bapxcoder_dir = self.project_path / '.bapXcoder'
        self.setup_project_structure()
    
    def setup_project_structure(self):
        """
        Setup the project-based memory structure

        Function: Creates the .bapXcoder directory and initializes project-specific files
        Connection: Links to session management and task tracking systems
        Purpose: Establish persistent project memory with todo.json and sessiontree.json
        Internal wiring: Sets up local storage for project-specific session data and task lists
        """
        self.bapxcoder_dir.mkdir(exist_ok=True)

        # Initialize project-specific files
        todo_file = self.bapxcoder_dir / 'todo.json'
        if not todo_file.exists():
            with open(todo_file, 'w') as f:
                json.dump([], f, indent=2)

        session_file = self.bapxcoder_dir / 'sessiontree.json'
        if not session_file.exists():
            with open(session_file, 'w') as f:
                json.dump({
                    'project_path': str(self.project_path),
                    'created_at': datetime.now().isoformat(),
                    'session_count': 0,
                    'last_session': None,
                    'active_files': [],
                    'file_stats': {},
                    'recent_files': [],
                    'project_type': 'unknown',
                    'dependencies': []
                }, f, indent=2)
    
    def get_project_tree(self, max_depth=3):
        """
        Get the project file tree structure

        Function: Builds a hierarchical representation of the project directory structure
        Connection: Links to file system navigation and UI rendering components
        Purpose: Provide project context and file structure visualization
        Internal wiring: Connects to UI components that display project hierarchy
        """
        tree = {}
        self._build_tree_recursive(self.project_path, tree, max_depth, 0)
        return tree
    
    def _build_tree_recursive(self, path, tree, max_depth, current_depth):
        """Build the tree recursively up to max depth"""
        if current_depth >= max_depth:
            return
            
        for item in path.iterdir():
            if item.name.startswith('.') and item.name not in ['.bapXcoder', '.git']:  # Skip hidden dirs except .git and .bapXcoder
                continue
                
            rel_path = item.relative_to(self.project_path)
            
            if item.is_dir():
                tree[str(rel_path)] = {
                    'type': 'directory',
                    'children': {},
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                self._build_tree_recursive(item, tree[str(rel_path)]['children'], max_depth, current_depth + 1)
            else:
                tree[str(rel_path)] = {
                    'type': 'file',
                    'size': item.stat().st_size,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    'extension': item.suffix
                }
    
    def get_file_content(self, file_path):
        """Get content of a file with encoding detection"""
        full_path = self.project_path / file_path
        
        if not full_path.exists() or full_path.is_dir():
            return None, "File does not exist"
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return None, f"Error reading file: {str(e)}"
        
        return None, "Could not decode file with common encodings"
    
    def save_file_content(self, file_path, content):
        """Save content to a file"""
        full_path = self.project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update session tree with file modification
            self.update_session_file_stats(file_path, len(content))
            return True, None
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    def update_session_file_stats(self, file_path, content_length):
        """Update session tree with file statistics"""
        session_file = self.bapxcoder_dir / 'sessiontree.json'
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
        except:
            data = {}
        
        # Initialize file_stats if it doesn't exist
        if 'file_stats' not in data:
            data['file_stats'] = {}

        # Update file stats
        rel_path = Path(file_path).relative_to(self.project_path).as_posix()
        data['file_stats'][rel_path] = {
            'size': content_length,
            'accessed': datetime.now().isoformat(),
            'active': True
        }
        
        # Update recent files (keep last 10)
        if 'recent_files' not in data:
            data['recent_files'] = []
            
        if rel_path not in data['recent_files']:
            data['recent_files'].insert(0, rel_path)
            data['recent_files'] = data['recent_files'][:10]  # Keep last 10 recent files
        else:
            # Move to front if already in list
            data['recent_files'].remove(rel_path)
            data['recent_files'].insert(0, rel_path)
        
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_recent_files(self):
        """Get recently accessed files"""
        session_file = self.bapxcoder_dir / 'sessiontree.json'
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            return data.get('recent_files', [])[:10]
        except:
            return []
    
    def search_in_project(self, query, file_extensions=None):
        """Search for text in project files"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt', '.java', '.cpp', '.c', '.go']
        
        results = []
        
        for ext in file_extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if '.bapXcoder' in str(file_path):  # Skip our own directories
                    continue
                    
                try:
                    content, error = self.get_file_content(file_path.relative_to(self.project_path))
                    if content and query.lower() in content.lower():
                        # Find line numbers where query appears
                        lines = content.lower().split('\n')
                        line_numbers = []
                        for i, line in enumerate(lines):
                            if query.lower() in line:
                                line_numbers.append(i + 1)
                        
                        results.append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'matches': len(line_numbers),
                            'line_numbers': line_numbers[:5]  # Show first 5 matches
                        })
                except:
                    continue
        
        return results

    def create_file(self, file_path, initial_content=""):
        """Create a new file in the project"""
        return self.save_file_content(file_path, initial_content)
    
    def delete_file(self, file_path):
        """Delete a file from the project"""
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return False, "File does not exist"
        
        try:
            os.remove(full_path)
            return True, None
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    def create_directory(self, dir_path):
        """Create a new directory in the project"""
        full_path = self.project_path / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            return True, None
        except Exception as e:
            return False, f"Error creating directory: {str(e)}"

    def get_project_stats(self):
        """Get overall project statistics"""
        stats = {
            'total_files': 0,
            'total_directories': 0,
            'total_size_bytes': 0,
            'file_types': {},
            'last_modified': None,
            'most_common_type': None
        }
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip .bapXcoder directory
            if '.bapXcoder' in root:
                dirs[:] = [d for d in dirs if d != '.bapXcoder']
                continue
                
            stats['total_directories'] += len(dirs)
            stats['total_files'] += len(files)
            
            for file in files:
                file_ext = Path(file).suffix
                stats['file_types'][file_ext] = stats['file_types'].get(file_ext, 0) + 1
                
                full_path = Path(root) / file
                stats['total_size_bytes'] += full_path.stat().st_size
        
        # Determine most common file type
        if stats['file_types']:
            stats['most_common_type'] = max(stats['file_types'], key=stats['file_types'].get)
        
        # Get last modified time
        try:
            all_items = []
            for root, dirs, files in os.walk(self.project_path):
                if '.bapXcoder' not in root:
                    for file in files:
                        full_path = Path(root) / file
                        all_items.append(full_path.stat().st_mtime)
                    for dir_name in dirs:
                        full_path = Path(root) / dir_name
                        all_items.append(full_path.stat().st_mtime)
            
            if all_items:
                stats['last_modified'] = datetime.fromtimestamp(max(all_items)).isoformat()
        except:
            pass
        
        return stats

    def get_file_content(self, file_path):
        """Get content of a file with encoding detection"""
        full_path = Path(file_path)

        # If file_path is relative, make it relative to project path
        if not full_path.is_absolute():
            full_path = self.project_path / file_path

        if not full_path.exists() or full_path.is_dir():
            return None, f"File does not exist: {file_path}"

        # Try different encodings to read the file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return None, f"Error reading file: {str(e)}"

        return None, f"Could not decode file with common encodings: {file_path}"

    def save_file_content(self, file_path, content):
        """Save content to a file"""
        full_path = Path(file_path)

        # If file_path is relative, make it relative to project path
        if not full_path.is_absolute():
            full_path = self.project_path / file_path

        try:
            # Ensure the directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Update session tree with file modification
            self.update_session_file_stats(str(full_path.relative_to(self.project_path)), len(content))
            return True, None
        except Exception as e:
            return False, f"Error saving file: {str(e)}"

    def create_file(self, file_path, initial_content=""):
        """Create a new file in the project"""
        full_path = Path(file_path)

        # If file_path is relative, make it relative to project path
        if not full_path.is_absolute():
            full_path = self.project_path / file_path

        # Ensure the directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(initial_content)
            return True, None
        except Exception as e:
            return False, f"Error creating file: {str(e)}"

    def create_directory(self, dir_path):
        """Create a new directory in the project"""
        full_path = Path(dir_path)

        # If dir_path is relative, make it relative to project path
        if not full_path.is_absolute():
            full_path = self.project_path / dir_path

        try:
            full_path.mkdir(parents=True, exist_ok=True)
            return True, None
        except Exception as e:
            return False, f"Error creating directory: {str(e)}"

    def search_in_project(self, query, file_extensions=None):
        """Search for text in project files"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt', '.java', '.cpp', '.c', '.go']

        results = []
        max_results = 50  # Limit to avoid too many results

        for ext in file_extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                # Skip .bapXcoder directory
                if '.bapXcoder' in str(file_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    if query.lower() in content.lower():
                        # Find line numbers where query appears
                        lines = content.split('\n')
                        line_numbers = []
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                line_numbers.append(i + 1)

                        results.append({
                            'file': str(file_path.relative_to(self.project_path)),
                            'matches': len(line_numbers),
                            'line_numbers': line_numbers[:10]  # Limit to first 10 matching lines
                        })

                        # Limit total results to avoid overloading
                        if len(results) >= max_results:
                            break
                except Exception:
                    continue  # Skip files that can't be read

        return results