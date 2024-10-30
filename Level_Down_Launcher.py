import os
import sys
import ctypes
import json
import time
import requests
import subprocess
import webbrowser
import feedparser  # For parsing the RSS feed
from rss_feed_widget import RSSFeedWidget
from wiki_update_scraper import fetch_updates  # Import the scraper function
# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QPushButton, QLabel,
    QStatusBar, QMessageBox, QFileDialog, QMenuBar, QAction, QSizePolicy, QSpacerItem,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt5.QtCore import QSize, Qt, QTimer, QUrl

# Custom module imports
from utils import load_config, save_config, load_version, save_version
from custom_web_engine import CustomWebEngineView
from login_dialog import LoginDialog
#from rss_feed import fetch_rss_feed  # Import the RSS feed function


# Paths to config and version files
CONFIG_PATH = "assets/config/config.json"
VERSION_PATH = "assets/config/version.json"

# Default configuration
default_config = {
    "ashita_exe": "",
    "windower_exe": "",
    "xi_loader_exe": "assets/config/xiLoader.exe"
}
default_version = {"launcher_version": "1.0.1"}

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
        self.progress_bar_label = QLabel(self)
        self.update_progress_bar(300, 100)
        layout.addWidget(self.progress_bar_label, alignment=Qt.AlignCenter | Qt.AlignBottom)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Launcher Version: {self.launcher_version}")

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
        # Add a spacer item to push the update list further down
        top_spacer = QSpacerItem(20, 200, QSizePolicy.Minimum, QSizePolicy.Fixed)  # Adjust height here as needed
        layout.addSpacerItem(top_spacer)

        # Fetch updates and create the list widget
        updates = fetch_updates()
        self.update_list_widget = QListWidget()
        self.update_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                border: 1px solid #5e5e5e;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #3e3e3e;
            }
        """)
    
        # Adjust the widget’s fixed size
        self.update_list_widget.setFixedHeight(150)  # Adjust height as needed
        self.update_list_widget.setFixedWidth(1180)   # Adjust width as needed

        # Populate the list widget with updates
        for update in updates:
            item_text = f"{update['title']}\n{update['description']}"
            list_item = QListWidgetItem(item_text)
            self.update_list_widget.addItem(list_item)

        # Add the update widget to the layout
        layout.addWidget(self.update_list_widget)
    def check_for_updates(self):
        """Checks for updates and starts the loading bar if necessary."""
        url = "https://api.github.com/repos/Dcannady03/LD-launcher/releases/latest"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                latest_version = response.json()["tag_name"]
                if latest_version != self.launcher_version:
                    self.start_loading_bar()
            else:
                print("Failed to fetch release information.")
                self.update_progress_bar(100)
        except Exception as e:
            print(f"Error checking for updates: {e}")
            self.update_progress_bar(100)

    def start_loading_bar(self):
        """Starts a simulated loading bar to update the UI."""
        self.progress = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(500)

    def update_progress(self):
        """Updates the progress bar visuals and increments the progress value."""
        if self.progress >= 100:
            self.progress_timer.stop()
            self.update_progress_bar(900, 40)
        else:
            self.progress += 25
            self.update_progress_bar(900, 40)

    def update_progress_bar(self, width, height):
        """Updates the loading bar's visual representation based on the progress."""
        image_path = {
            0: "assets/images/loadingbar 0.png",
            10: "assets/images/loadingbar 10 copy.png",
            25: "assets/images/loadingbar 25 copy.png",
            50: "assets/images/loadingbar 50 copy.png",
            75: "assets/images/loadingbar 75 copy.png",
            100: "assets/images/loadingbar 1000 copy.png"
        }.get(self.progress, "assets/images/loadingbar 0.png")

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.progress_bar_label.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.progress_bar_label.setFixedSize(width, height)
            self.progress_bar_label.setAlignment(Qt.AlignCenter)
        else:
            print("Failed to load progress bar image.")

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


    

    #def add_web_browser(self, layout):
        # Create a spacer item to push the news view down
     #   spacer = QSpacerItem(20, 300, QSizePolicy.Minimum, QSizePolicy.Fixed)  # Adjust height here as needed
      #  layout.addSpacerItem(spacer)
    
        # Create the web view
       # news_view = CustomWebEngineView()
      #  news_view.setUrl(QUrl("https://cdn.mysitemapgenerator.com/shareapi/rss/2610832342"))
       # news_view.setFixedHeight(100)
    
        # Add the web view to the layout
        #layout.addWidget(news_view)


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