import os
import sys
import ctypes
import json
import time
import requests
import subprocess
import threading 
import webbrowser
import feedparser  # For parsing the RSS feed
from rss_feed_widget import RSSFeedWidget
from wiki_update_scraper import fetch_updates  # Import the scraper function
# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLabel,
    QStatusBar, QMessageBox, QFileDialog, QMenuBar, QAction, QSizePolicy, QSpacerItem,
    QListWidget, QListWidgetItem, QFrame, QScrollArea,QTextEdit
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import QSize, Qt, QTimer, QUrl

# Custom module imports
from utils import load_config, save_config, load_version, save_version
from custom_web_engine import CustomWebEngineView
from login_dialog import LoginDialog
#from rss_feed import fetch_rss_feed  # Import the RSS feed function
from update_manager import check_for_update, get_remote_version, get_local_version



# Paths to config and version files
CONFIG_PATH = "assets/config/config.json"
VERSION_PATH = "assets/config/version.json"
previous_manifest_path = "assets/config/previous_manifest.json"
#base_file_url = "https://raw.githubusercontent.com/Dcannady03/Level-Down-Launcher/update/update_files"



# Default configuration
default_config = {
    "ashita_exe": "",
    "windower_exe": "",
    "xi_loader_exe": "assets/config/xiLoader.exe"
}
default_version = {"version": "1.0."}

# Ensure configuration files exist with default values if missing
def create_file_if_not_exists(path, default_content):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            json.dump(default_content, file, indent=4)

create_file_if_not_exists(CONFIG_PATH, default_config)
create_file_if_not_exists(VERSION_PATH, default_version)



class LauncherMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.launcher_version = load_version()
        self.config = load_config()
        self.progress = 0
        self.setWindowTitle(f"Level Down Launcher - Version {self.launcher_version}")
        self.setFixedSize(1200, 800)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.set_background_image()
        self.setup_ui()
        self.check_for_updates()

        # Set up the timer to refresh updates periodically
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.refresh_updates)
        self.update_timer.start(1000)  # Refresh every 10 minutes (600,000 ms)
        # utils.py or wherever load_version is defined
    def load_version():
        """Loads the version information from version.json."""
        version_path = "assets/config/version.json"
        if os.path.exists(version_path):
            with open(version_path, "r") as file:
                data = json.load(file)
                return data.get("version", "0.0")  # Fallback to "0.0" if version key is missing
        else:
            return "0.0"  # Fallback if version.json is missing

    def check_for_updates(self):
        """Checks for updates and initiates the update process if needed."""
        local_version = get_local_version()
        remote_version = get_remote_version()

        if remote_version and remote_version > local_version:
            print(f"New version {remote_version} available. Starting update...")
            self.start_loading_bar()  # Starts the progress bar animation
            update_thread = threading.Thread(target=self.perform_update)
            update_thread.start()
        else:
            print("No updates found. Application is up to date.")
            self.update_progress(100)  # Set the progress bar to full if no update is needed

    def perform_update(self):
        """Performs the update process and provides feedback on progress."""
        # Simulate the update process with step-by-step progress updates
        try:
            total_steps = 5  # Set the number of steps or files for the update process
            for step in range(1, total_steps + 1):
                time.sleep(1)  # Simulate a time delay for each step
                progress = int((step / total_steps) * 100)
                self.update_progress(progress)  # Update progress incrementally

            print("Update complete.")
        except Exception as e:
            print(f"Update failed: {e}")
        finally:
            self.update_progress(100)  # Ensure the progress bar is set to full at the end


    def setup_menu_bar(self):
        """Set up dark-themed menu bar."""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("QMenuBar { background-color: #2e2e2e; color: #ffffff; }")
        file_menu = menu_bar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        settings_menu = menu_bar.addMenu('Settings')
        ashita_action = QAction('Set Ashita Executable', self)
        ashita_action.triggered.connect(self.set_ashita_exe)
        settings_menu.addAction(ashita_action)

        windower_action = QAction('Set Windower Executable', self)
        windower_action.triggered.connect(self.set_windower_exe)
        settings_menu.addAction(windower_action)

    
    def set_background_image(self):
        background_path = os.path.join(os.getcwd(), "assets", "images", "wallpaper.png")
        background_label = QLabel(self.central_widget)
        background_pixmap = QPixmap(background_path)

        if not background_pixmap.isNull():
            scaled_background = background_pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            background_label.setPixmap(scaled_background)
            background_label.resize(self.size())
            background_label.lower()
        else:
            QMessageBox.warning(self, "Error", f"Failed to load background image from {background_path}")
    
    def setup_ui(self):
        """Set up UI layout and components."""
        layout = QVBoxLayout(self.central_widget)
        self.setup_menu_bar()
        top_layout = QHBoxLayout()
        self.add_sidebar_with_buttons(top_layout)
        layout.addLayout(top_layout)
        self.add_updates(layout)

        # Create a main progress bar container
        self.progress_bar_container = QWidget(self)
        self.progress_bar_container.setFixedSize(900, 10)
        self.progress_bar_container.setStyleSheet("background-color: #3e3e3e; border: 2px solid #2e2e2e;")

        # Create a fill widget inside the container
        self.progress_fill = QWidget(self.progress_bar_container)
        self.progress_fill.setStyleSheet("background-color: #0078d4;")
        self.progress_fill.resize(0, 10)  # Start with no fill

        layout.addWidget(self.progress_bar_container, alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Launcher Version: {self.launcher_version}")

    def update_progress(self, percentage_progress=0):
        """Update the width of the fill widget to simulate progress."""
        max_width = self.progress_bar_container.width()
        new_width = int(max_width * (percentage_progress / 100))
        self.progress_fill.resize(new_width, 10)  # Adjust height as needed

    def create_button_with_image(self, image_path, callback, image_below_path, button_size=(50, 50), icon_size=(50, 50), image_below_size=(100, 40)):
        button_with_image_layout = QVBoxLayout()
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(image_path)))
        button.setIconSize(QSize(*icon_size))
        button.setFixedSize(QSize(*button_size))
        button.setStyleSheet("QPushButton { background-color: transparent; border: none; }")
        button.clicked.connect(callback)

        image_label = QLabel()
        image_label.setPixmap(QPixmap(image_below_path).scaled(QSize(*image_below_size), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignCenter)
        button_with_image_layout.addWidget(button)
        button_with_image_layout.addWidget(image_label)

        return button_with_image_layout
    
    
       
    def add_updates(self, layout):
        top_spacer = QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addSpacerItem(top_spacer)

        # Create a QTextEdit for displaying updates with scrolling enabled
        self.update_text_edit = QTextEdit()
        self.update_text_edit.setReadOnly(True)  # Make it read-only
        self.update_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2e2e2e;
                color: #ffffff;
                border: 1px solid #5e5e5e;
                font-size: 14px;  /* Adjust this value to change font size */
                padding: 10px;
            }
        """)

        # Set the height and enable scroll bars
        self.update_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.update_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.update_text_edit.setFixedWidth(1180)
        #self.update_text_edit.setFixedHeight(300)  # Adjust the height for better readability

        # Fetch and display updates
        self.refresh_updates()

        # Add the QTextEdit to the layout directly
        layout.addWidget(self.update_text_edit)
    # Save JSON file
    
    def fetch_updates(self):
        # URL of the update notification file in your GitHub repository
        url = "https://raw.githubusercontent.com/Dcannady03/discord-update-bot/main/update_notification.txt"
        updates = []

        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text.strip()
                updates.append({"title": "Discord Update", "description": content})
            else:
                updates.append({"title": "No New Updates", "description": "No new updates from Discord at this time."})
        except requests.RequestException as e:
            print(f"Error fetching updates: {e}")
            updates.append({"title": "Error", "description": "Failed to fetch updates due to a network error."})
        except Exception as e:
            print(f"Unexpected error: {e}")
            updates.append({"title": "Error", "description": "An unexpected error occurred while fetching updates."})

        return updates

    def refresh_updates(self):
        """Refreshes the update text edit widget only if there are new updates."""
        updates = self.fetch_updates()
    
        # Combine all updates into a single text string
        new_content = ""
        for update in updates:
            new_content += f"{update['title']}\n{update['description']}\n\n"

        # Check if the current content matches the new content
        if self.update_text_edit.toPlainText().strip() == new_content.strip():
            # Skip update if content hasn't changed
            #print("No new updates, skipping refresh.")
            return
    
        # Update the text if there's new content
        self.update_text_edit.clear()  # Clear the text box before reloading
        self.update_text_edit.setPlainText(new_content)
        #print("Updates refreshed.")
    
    

    def add_sidebar_with_buttons(self, layout):
        sidebar_widget = QWidget()
        grid_layout = QGridLayout()
        sidebar_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        buttons = [
            ('assets/images/ashita.png', self.launch_ashita, 'assets/images/ashitatxt.png'),
            ('assets/images/windower.png', self.launch_windower, 'assets/images/windowertxt.png'),
            ('assets/images/launcher.png', self.open_login_dialog, 'assets/images/stand copy.png'),
            ('assets/images/wiki.png', self.open_wiki, 'assets/images/wikitxt.png')
        ]

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, (image_path, callback, image_below_path) in enumerate(buttons):
            button_layout = self.create_button_with_image(image_path, callback, image_below_path, button_size=(75, 75), icon_size=(75, 75), image_below_size=(90, 60))
            grid_layout.addLayout(button_layout, *positions[i])

        grid_layout.setContentsMargins(35, 50, 0, 0)
        sidebar_widget.setLayout(grid_layout)
        layout.addWidget(sidebar_widget, alignment=Qt.AlignLeft)

    def launch_ashita(self):
        if self.config.get("ashita_exe"):
            try:
                subprocess.Popen([self.config["ashita_exe"]])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to launch Ashita: {e}")
        else:
            QMessageBox.warning(self, "Executable Not Set", "Please set the Ashita executable in Settings.")

    # Method to launch Windower
    def launch_windower(self):
        if self.config.get("windower_exe"):
            try:
                subprocess.Popen([self.config["windower_exe"]])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to launch Windower: {e}")
        else:
            QMessageBox.warning(self, "Executable Not Set", "Please set the Windower executable in Settings.")

    def set_ashita_exe(self):
        """Set the executable path for Ashita."""
        exe_path, _ = QFileDialog.getOpenFileName(self, "Select Ashita Executable", "", "Executable Files (*.exe)")
        if exe_path:
            self.config["ashita_exe"] = exe_path
            save_config(self.config)
            QMessageBox.information(self, "Executable Set", "Ashita executable set successfully!")

    def set_windower_exe(self):
        """Set the executable path for Windower."""
        exe_path, _ = QFileDialog.getOpenFileName(self, "Select Windower Executable", "", "Executable Files (*.exe)")
        if exe_path:
            self.config["windower_exe"] = exe_path
            save_config(self.config)
            QMessageBox.information(self, "Executable Set", "Windower executable set successfully!")

    def open_login_dialog(self):
        login_dialog = LoginDialog(self.config, self)
        login_dialog.exec_()

    def open_wiki(self):
        webbrowser.open("https://ffxileveldown.fandom.com/wiki/FFXILevelDown_Wiki")