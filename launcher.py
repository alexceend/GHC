import sys
import os
import csv
import ctypes
import ctypes.wintypes
import tempfile
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QMessageBox, QHeaderView, QFileDialog, QLabel,
    QBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PIL.ImageQt import ImageQt





print("Starting launcher...")
# -------- PATHS --------
APP_DIR = os.path.join(
    os.environ["USERPROFILE"], "Documents", "GameTimeCounter"
)
os.makedirs(APP_DIR, exist_ok=True)

CSV_PATH = os.path.join(APP_DIR, "games.csv")
PLAYTIME_PATH = os.path.join(APP_DIR, "playtime.txt")

# Create CSV if missing
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["exe_name", "proc_name"])


class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Time Counter – Launcher")

        #self.resize(500, 350)
        self.showMaximized()
        
        # TIMER
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_playtime_table)
        self.timer.start(10_000)
        


        self.layout = QVBoxLayout(self)

        # ---- TABLE ----
        self.table = QTableWidget(0, 3)
        self.table.setColumnWidth(0, 250)  # Game Name
        self.table.setColumnWidth(1, 250)  # Playtime
        self.table.setColumnHidden(2, True)  # hide exe path column
        self.table.setHorizontalHeaderLabels(["Game Name", "Playtime"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setIconSize(QPixmap(96,96).size())
        self.table.verticalHeader().setDefaultSectionSize(128)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # CSS
        self.table.setStyleSheet("""
        QTableWidget::item {
            position: center;
            text-align: center;
        }
        
        QTableWidget::item:hover {
            background-color: white;
            color:black;
        }
        
        QTableWidget::item:selected {
            background-color: #3399BB; /*Blue*/
            color: black;
        }
        
        """)

        
        self.layout.addWidget(self.table)

        # LAUNCH
        
        launch_layout = QHBoxLayout()
        launch_btn = QPushButton("▶ Launch selected")
        launch_btn.clicked.connect(self.launch_selected)
        launch_layout.addWidget(launch_btn)
        self.layout.addLayout(launch_layout)

        # ---- INPUTS ----
        input_layout = QHBoxLayout()
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("game.exe")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.select_exe)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Game Name")

        input_layout.addWidget(self.exe_input)
        input_layout.addWidget(browse_btn)
        input_layout.addWidget(self.name_input)
        self.layout.addLayout(input_layout)

        # ---- BUTTONS ----
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("Add Game")
        add_btn.clicked.connect(self.add_game)

        del_btn = QPushButton("Delete Selected")
        del_btn.clicked.connect(self.delete_selected)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)

        self.layout.addLayout(btn_layout)

        
        self.load_games()
        self.update_playtime_table()

    # -------- CSV LOGIC --------
    def load_games(self):
        self.table.setRowCount(0)
        playtime = self.load_playtime()

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                exe = row["exe_name"]
                name = row["proc_name"]
                seconds = playtime.get(name, 0)
                icon = self.get_icon_from_exe(exe)
                self.add_row(row["exe_name"], name, seconds=seconds, icon=icon)


    def load_playtime(self):
        playtime = {}
        if os.path.exists(PLAYTIME_PATH):
            with open(PLAYTIME_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        name, value = line.strip().split(":", 1)
                        try:
                            playtime[name] = float(value)
                        except ValueError:
                            playtime[name] = 0
        return playtime
    
    def save_games(self):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["exe_name", "proc_name"])
            for row in range(self.table.rowCount()):
                exe = self.table.item(row, 2).text()
                name = self.table.item(row, 0).text()
                writer.writerow([exe, name])

    # -------- UI ACTION

    def add_game(self):
        exe = self.exe_input.text().strip()
        exe = os.path.abspath(exe)
        name = self.name_input.text().strip()

        if not exe or not name:
            QMessageBox.warning(self, "Error", "Both fields are required")
            return

        if not exe.endswith(".exe"):
            QMessageBox.warning(self, "Error", "Executable must end with .exe")
            return

        icon = self.get_icon_from_exe(exe)
        self.add_row(exe, name, icon=icon)
        self.save_games()

        self.exe_input.clear()
        self.name_input.clear()

    def delete_selected(self):
        rows = sorted(
            {i.row() for i in self.table.selectedIndexes()},
            reverse=True
        )

        if not rows:
            QMessageBox.information(self, "Info", "No selection")
            return

        for row in rows:
            self.table.removeRow(row)

        self.save_games()
      
    def add_row(self, exe, name, seconds=0, icon=None):
        row = self.table.rowCount()
        self.table.insertRow(row)

        item_name = QTableWidgetItem(name)
        if icon:
            item_name.setIcon(icon)
           
            
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)

            
        item_name.setFont(font)
            
        #item_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter) # center text
        item_name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.table.setItem(row, 0, item_name)

        # PLAYTIME 
        item_time = QTableWidgetItem(self.format_time(seconds))
        item_time.setFont(font)
        
        item_time.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item_time)
        
        item_exe = QTableWidgetItem(exe)  # store exe path in hidden column
        self.table.setItem(row, 2, item_exe)
        
    
    def select_exe(self):
        filep, _ = QFileDialog.getOpenFileName(
            self,
            "Select Game's EXE",
            "",
            "Executable Files (*.exe)"
        )
        if filep:
            self.exe_input.setText(filep)
    
    def get_icon_from_exe(self, exe_path):
        exe_path = os.path.abspath(exe_path)
        
        if not os.path.exists(exe_path):
            print(f"File does not exist -> {exe_path}")
            return QIcon()

        try:
            import win32ui
            import win32gui
            import win32con
            import win32api
            from PIL import Image
            
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            
            large, small = win32gui.ExtractIconEx(exe_path,0)
            win32gui.DestroyIcon(small[0])
            
            hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_x )
            hdc = hdc.CreateCompatibleDC()

            hdc.SelectObject( hbmp )
            hdc.DrawIcon( (0,0), large[0] )

            bmpstr = hbmp.GetBitmapBits(True)
            icon = Image.frombuffer(
                'RGBA',
                (32,32),
                bmpstr, 'raw', 'BGRA', 0, 1
            )
            
            qt_image = ImageQt(icon)  # Convert PIL Image to Qt Image
            pixmap = QPixmap.fromImage(qt_image)
            return QIcon(pixmap)
            
        except Exception as e:
            print("Icon extraction failed:", e)

        return QIcon()
   
    def launch_selected(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.information(self, "Info", "Select a game first")
            return

        exe = self.table.item(row, 2).text()
        if not os.path.exists(exe):
            QMessageBox.warning(self, "Error", "Executable not found")
            return

        try:
            subprocess.Popen(exe)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
   
    # AUX
    def format_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}h {m}m {s}s"
        
    def update_playtime_table(self):
        playtime = self.load_playtime()
        
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            seconds = playtime.get(name, 0)
            self.table.item(row, 1).setText(
                self.format_time(seconds)
        )



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Launcher()
    win.show()
    sys.exit(app.exec())
