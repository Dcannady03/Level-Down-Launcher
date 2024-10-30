import feedparser
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RSSFeedWidget(QWidget):
    def __init__(self, rss_url, parent=None):
        super().__init__(parent)
        self.rss_url = rss_url
        self.init_ui()

    def init_ui(self):
        # Main layout with scroll area for feed entries
        layout = QVBoxLayout(self)
        
        # Scroll area to contain the RSS feed content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        # Content widget inside the scroll area
        content_widget = QWidget()
        self.feed_layout = QVBoxLayout(content_widget)
        self.feed_layout.setAlignment(Qt.AlignTop)

        # Add the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Fetch and display the RSS feed entries
        self.fetch_and_display_feed()

    def fetch_and_display_feed(self):
        # Parse the RSS feed from the URL
        feed = feedparser.parse(self.rss_url)
        
        # Loop through each entry and create a styled widget for each
        for entry in feed.entries:
            # Create a frame for each entry
            entry_frame = QFrame()
            entry_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            entry_frame.setStyleSheet("background-color: #2e2e2e; border: 1px solid #444; margin-bottom: 10px; padding: 10px;")
            
            entry_layout = QVBoxLayout(entry_frame)
            
            # Title label
            title_label = QLabel(entry.title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
            entry_layout.addWidget(title_label)

            # Summary/description label
            description_label = QLabel(entry.get("summary", ""))
            description_label.setFont(QFont("Arial", 10))
            description_label.setWordWrap(True)
            description_label.setStyleSheet("color: #cccccc; margin-bottom: 5px;")
            entry_layout.addWidget(description_label)

            # "Read More" button to open the link in a browser
            link_button = QPushButton("Read More")
            link_button.setStyleSheet("color: #4a90e2; background-color: #333; border: none; padding: 5px 10px;")
            link_button.clicked.connect(lambda _, url=entry.link: self.open_link(url))
            entry_layout.addWidget(link_button, alignment=Qt.AlignLeft)

            # Add the completed entry frame to the feed layout
            self.feed_layout.addWidget(entry_frame)

    def open_link(self, url):
        # Open the provided URL in the default web browser
        import webbrowser
        webbrowser.open(url)
