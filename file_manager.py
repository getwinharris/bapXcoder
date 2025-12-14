from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import os
from pathlib import Path
import subprocess
import time
from project_explorer import ProjectExplorer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bapxcoder-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global project explorer instance
current_explorer = None

@socketio.on('initialize_project')
def handle_initialize_project(data):
    """Initialize a project with the project explorer"""
    project_path = data.get('project_path', os.getcwd())
    global current_explorer
    try:
        current_explorer = ProjectExplorer(project_path)
        # Send project tree
        project_tree = current_explorer.get_project_tree()
        recent_files = current_explorer.get_recent_files()
        project_stats = current_explorer.get_project_stats()
        
        emit('project_initialized', {
            'tree': project_tree,
            'recent_files': recent_files,
            'stats': project_stats,
            'project_path': project_path
        })
    except Exception as e:
        emit('error', {'message': f'Error initializing project: {str(e)}'})

@socketio.on('open_file')
def handle_open_file(data):
    """Open a file for editing"""
    file_path = data.get('file_path', '')
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        content, error = current_explorer.get_file_content(file_path)
        if content is not None:
            emit('file_opened', {
                'file_path': file_path,
                'content': content,
                'success': True
            })
        else:
            emit('file_error', {'message': error})
    except Exception as e:
        emit('file_error', {'message': f'Error opening file: {str(e)}'})

@socketio.on('save_file')
def handle_save_file(data):
    """Save a file"""
    file_path = data.get('file_path', '')
    content = data.get('content', '')
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        success, error = current_explorer.save_file_content(file_path, content)
        if success:
            emit('file_saved', {
                'file_path': file_path,
                'success': True
            })
        else:
            emit('file_error', {'message': error})
    except Exception as e:
        emit('file_error', {'message': f'Error saving file: {str(e)}'})

@socketio.on('create_file')
def handle_create_file(data):
    """Create a new file"""
    file_path = data.get('file_path', '')
    initial_content = data.get('content', '')
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        success, error = current_explorer.create_file(file_path, initial_content)
        if success:
            emit('file_created', {
                'file_path': file_path,
                'success': True
            })
        else:
            emit('file_error', {'message': error})
    except Exception as e:
        emit('file_error', {'message': f'Error creating file: {str(e)}'})

@socketio.on('delete_file')
def handle_delete_file(data):
    """Delete a file"""
    file_path = data.get('file_path', '')
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        success, error = current_explorer.delete_file(file_path)
        if success:
            emit('file_deleted', {
                'file_path': file_path,
                'success': True
            })
        else:
            emit('file_error', {'message': error})
    except Exception as e:
        emit('file_error', {'message': f'Error deleting file: {str(e)}'})

@socketio.on('create_directory')
def handle_create_directory(data):
    """Create a new directory"""
    dir_path = data.get('dir_path', '')
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        success, error = current_explorer.create_directory(dir_path)
        if success:
            emit('directory_created', {
                'dir_path': dir_path,
                'success': True
            })
        else:
            emit('directory_error', {'message': error})
    except Exception as e:
        emit('directory_error', {'message': f'Error creating directory: {str(e)}'})

@socketio.on('search_files')
def handle_search_files(data):
    """Search in project files"""
    query = data.get('query', '')
    file_extensions = data.get('extensions', None)
    
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        results = current_explorer.search_in_project(query, file_extensions)
        emit('search_results', {
            'query': query,
            'results': results
        })
    except Exception as e:
        emit('search_error', {'message': f'Error searching files: {str(e)}'})

@socketio.on('get_project_stats')
def handle_get_project_stats(data):
    """Get project statistics"""
    if not current_explorer:
        emit('error', {'message': 'Project not initialized'})
        return
    
    try:
        stats = current_explorer.get_project_stats()
        emit('project_stats', stats)
    except Exception as e:
        emit('error', {'message': f'Error getting project stats: {str(e)}'})

if __name__ == "__main__":
    # This would be imported in the main application
    pass