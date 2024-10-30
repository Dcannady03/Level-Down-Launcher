# login_dialog.py

import os
import subprocess
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox

class LoginDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Login to Final Fantasy XI")
        self.setFixedSize(500, 200)

        # Apply dark theme stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
                color: #ffffff;
            }
            QLabel, QLineEdit, QComboBox, QPushButton {
                color: #ffffff;
                background-color: #4b4b4b;
                border: 1px solid #5e5e5e;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6b6b6b;
            }
        """)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Input fields
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        # Server selection
        self.server_combo = QComboBox()
        self.server_combo.addItem("Level Down 75", "ffxileveldown75.ddns.net")
        self.server_combo.addItem("Level Down 99", "ffxileveldown.ddns.net")
        form_layout.addRow("Server:", self.server_combo)
        layout.addLayout(form_layout)

        # Buttons
        login_button = QPushButton("Log In")
        login_button.clicked.connect(self.login)
        create_account_button = QPushButton("Create Account")
        create_account_button.clicked.connect(self.create_account)
        layout.addWidget(login_button)
        layout.addWidget(create_account_button)
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        server = self.server_combo.currentData()

        if username and password:
            xi_loader_path = self.config.get("xi_loader_exe", "")
            if os.path.exists(xi_loader_path):
                subprocess.Popen([xi_loader_path, f"--server", server, f"--username", username, f"--password", password])
            else:
                QMessageBox.warning(self, "Error", "XI Loader executable not found!")
        else:
            QMessageBox.warning(self, "Error", "Please enter both username and password!")

    def create_account(self):
        server = self.server_combo.currentData()
        xi_loader_path = self.config.get("xi_loader_exe", "")
        if os.path.exists(xi_loader_path):
            subprocess.Popen([xi_loader_path, f"--server", server])
        else:
            QMessageBox.warning(self, "Error", "XI Loader executable not found!")



