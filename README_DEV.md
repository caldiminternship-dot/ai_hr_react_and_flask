# Development Guide - Fixing Cache Issues

## Problem
When you make changes to Python files (like `response_analyzer.py`, `question_generator.py`, etc.), the changes don't appear when you refresh the app. This is because Python caches imported modules.

## Solutions

### Option 1: Quick Fix (Recommended)
Run the cache clearing script whenever you make changes:

```bash
# Clear cache
python clear_cache.py

# Then restart Streamlit
streamlit run app.py
```

### Option 2: Automated Restart (Linux/Mac)
Use the restart script that clears cache and restarts automatically:

```bash
chmod +x restart_app.sh
./restart_app.sh
```

### Option 3: Windows Users
```cmd
clear_cache.py
streamlit run app.py --server.runOnSave true
```

Or double-click `restart_app.bat`

### Option 4: Manual Cache Clearing
1. Stop Streamlit (Ctrl+C)
2. Delete all `__pycache__` folders:
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```
3. Restart Streamlit:
   ```bash
   streamlit run app.py
   ```

## Best Practices During Development

### 1. Enable Auto-Reload in Streamlit
When starting Streamlit, use the `--server.runOnSave` flag:
```bash
streamlit run app.py --server.runOnSave true
```

This makes Streamlit automatically reload when you save `app.py`, but it won't reload imported modules unless you clear the cache.

### 2. Test Changes
After clearing cache and restarting:
1. Make a small test change (like adding a print statement)
2. Verify the change appears
3. Continue development

### 3. Use the Clear Cache Button in Streamlit
- Press `C` in the browser while Streamlit is running
- Or click the hamburger menu → Clear Cache

## Common Issues

### Issue: Changes still not appearing
**Solution:**
1. Clear Python cache: `python clear_cache.py`
2. Clear Streamlit cache: Delete `~/.streamlit/cache`
3. Fully stop and restart Streamlit (don't just refresh)

### Issue: Import errors after clearing cache
**Solution:**
Ensure all files are saved and there are no syntax errors:
```bash
python -m py_compile your_file.py
```

### Issue: Database changes not reflecting
**Solution:**
Database schema changes require database migration:
```bash
python init_db_script.py
```

## Development Workflow

**Recommended workflow:**

1. Make your code changes
2. Save all files
3. Run `python clear_cache.py`
4. Press `C` in Streamlit browser to clear Streamlit cache
5. Refresh the browser

**Or use the automated script:**
1. Make your code changes
2. Run `./restart_app.sh` (Linux/Mac) or `restart_app.bat` (Windows)
3. Browser will automatically reconnect

## Why This Happens

Python's import system caches modules to improve performance. Once a module is imported with `import module_name`, Python stores it in `sys.modules` and won't reload it even if the file changes.

Streamlit's hot-reload feature only reloads the main script (`app.py`), not imported modules.

## Files That Need Cache Clearing

Any changes to these files require cache clearing:
- `response_analyzer.py`
- `question_generator.py`
- `report_manager.py`
- `skill_mapper.py`
- `resume_parser.py`
- `utils.py`
- `config.py`
- `auth.py`
- `models.py`

Changes to `app.py` usually reflect automatically with `--server.runOnSave true`.
