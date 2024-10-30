# Level_Down_Launcher.py

import os
import requests
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QStatusBar, QProgressBar, QWidget, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from utils import load_config, save_config, load_version
import subprocess

class LauncherMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load version and config
        self.launcher_version = load_version()
        self.config = load_config()
        self.setWindowTitle(f"Level Down Launcher - Version {self.launcher_version}")
        self.setFixedSize(1200, 800)

        # Setup central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Set background
        self.set_background_image(layout)

        # Status bar with version info and progress bar for updates
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Launcher Version: {self.launcher_version}")

        # Progress bar setup
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress = 0

        # Begin checking for updates
        self.check_for_updates()

    def set_background_image(self, layout):
        # Path to background image
        background_path = os.path.join(os.getcwd(), "assets", "images", "wallpaper.png")
        background_label = QLabel(self.central_widget)
        pixmap = QPixmap(background_path)

        if pixmap.isNull():
            background_label.setText("Background could not be loaded.")
            background_label.setAlignment(Qt.AlignCenter)
        else:
            scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            background_label.setPixmap(scaled_pixmap)
        
        layout.addWidget(background_label)

    def check_for_updates(self):
        print("Checking for updates on GitHub")
        url = "https://api.github.com/repos/Dcannady03/LD-launcher/releases/latest"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release["tag_name"]
                print(f"Latest version: {latest_version}")
                
                # Simulate loading with timer
                self.progress_timer = QTimer(self)
                self.progress_timer.timeout.connect(self.update_progress)
                self.progress_timer.start(100)
            else:
                print("Failed to fetch release information.")
                self.progress_bar.setValue(100)

        except Exception as e:
            print(f"Error checking for updates: {e}")
            self.progress_bar.setValue(100)

    def update_progress(self):
        if self.progress < 100:
            self.progress += 10
            self.progress_bar.setValue(self.progress)
        else:
            self.progress_timer.stop()
            print("Progress complete")
            # Optional: show message or log if update check completed
