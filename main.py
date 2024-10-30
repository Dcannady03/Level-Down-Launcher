# main.py
import sys
from PyQt5.QtWidgets import QApplication
from update_manager import check_for_update
from Level_Down_Launcher import LauncherMainWindow

class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        print("ApplicationManager initialized")

        # Call update check
        check_for_update()
        print("Update check completed")

        # Launch main application
        self.launch_main_window()

    def launch_main_window(self):
        print("Launching main window")
        self.main_window = LauncherMainWindow()
        self.main_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app_manager = ApplicationManager()




