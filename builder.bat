@echo off

echo Using Python:
python --version

echo Building counter EXE...
python -m PyInstaller --onefile --noconsole --name games_hour_counter_tray counter.py

echo Building launcher EXE...
python -m PyInstaller --onefile --noconsole --name games_hour_counter_launcher launcher.py


pause
