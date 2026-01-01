@echo off
set PYTHON="C:\Users\alexc\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe"

echo Using Python:
%PYTHON% --version

echo Building counter EXE...
%PYTHON% -m PyInstaller --onefile --noconsole --name games_hour_counter_tray counter.py

echo Building launcher EXE...
%PYTHON% -m PyInstaller --onefile --noconsole --name games_hour_counter_launcher launcher.py


pause
