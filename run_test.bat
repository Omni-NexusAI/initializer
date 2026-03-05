@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
python -u test_whisper2.py 2>&1
echo Exit code: %ERRORLEVEL%
