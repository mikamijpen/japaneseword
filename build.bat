@echo off
CALL conda activate tools
pyinstaller --onefile --windowed --name JapaneseWordApp ui.py
pause 