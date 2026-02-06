@echo off
REM Script to properly restart Streamlit with cache clearing (Windows)

echo Clearing Python cache...
python clear_cache.py

echo Clearing Streamlit cache...
rmdir /s /q "%USERPROFILE%\.streamlit\cache" 2>nul

echo.
echo Cache cleared!
echo Please restart Streamlit manually:
echo   streamlit run app.py --server.runOnSave true
echo.
pause
