"""
Development Helper - Hot Module Reloading
Add this to the top of app.py during development to enable hot reloading
"""
import importlib
import sys

def reload_modules():
    """Reload all custom modules to reflect code changes"""
    modules_to_reload = [
        'response_analyzer',
        'question_generator',
        'report_manager',
        'skill_mapper',
        'resume_parser',
        'utils',
        'config',
        'auth',
        'models'
    ]

    reloaded = []
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
                reloaded.append(module_name)
            except Exception as e:
                print(f"Warning: Could not reload {module_name}: {e}")

    return reloaded

# Optional: Auto-detect file changes
def watch_for_changes():
    """Watch for file changes and trigger reload (development only)"""
    import os
    import time

    watched_files = [
        'response_analyzer.py',
        'question_generator.py',
        'report_manager.py',
        'skill_mapper.py',
        'resume_parser.py',
        'utils.py',
        'config.py',
        'auth.py',
        'models.py'
    ]

    file_mtimes = {}
    for file in watched_files:
        if os.path.exists(file):
            file_mtimes[file] = os.path.getmtime(file)

    return file_mtimes

def check_for_updates(previous_mtimes):
    """Check if any watched files have been modified"""
    changed = []
    for file, old_mtime in previous_mtimes.items():
        if os.path.exists(file):
            current_mtime = os.path.getmtime(file)
            if current_mtime > old_mtime:
                changed.append(file)
    return changed
