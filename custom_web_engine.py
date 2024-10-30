# custom_web_engine.py

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class CustomWebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set custom settings for the web engine
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)

        # Optional: Connect console messages to a handler
        self.page().javaScriptConsoleMessage = self.handle_js_console_messages

    def handle_js_console_messages(self, level, message, line_number, source_id):
        if level == 2:  # Only print errors
            print(f"JavaScript error at line {line_number}: {message}")

