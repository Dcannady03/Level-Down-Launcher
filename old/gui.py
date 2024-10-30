from PyQt5.QtWidgets import QGridLayout,QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidgetItem, QStackedWidget, QListWidget, QFileDialog, QMessageBox, QDialog, QLineEdit, QScrollArea, QCheckBox, QTabWidget, QComboBox, QFormLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
import os
import configparser
from profile_manager import load_profile, save_profile
from settings_manager import load_settings, save_settings
from functools import partial
from addon_plugin_manager import AddonPluginManager
import shutil  # To use for copying files
import sys
import subprocess

def resource_path(relative_path):
        """ Get the absolute path to a resource, works for dev and for PyInstaller """
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller creates a temp folder and stores files in it
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            return os.path.join(os.path.abspath("."), relative_path)

class FantasyGatewayGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fantasy Gateway")
        self.setMinimumSize(800, 600)

        # Initialize AddonPluginManager with correct paths
        self.manager = AddonPluginManager(addon_folder='./addons', plugin_folder='./plugins', config_file='config.json')
        
        # Check if Fantasy_Gateway.txt exists in the scripts folder
        self.check_and_copy_default_config()

        # Load settings
        self.settings = load_settings()

        # Initialize the UI
        self.init_ui()

        # Apply the current theme
        if self.settings['theme'] == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
 

        # Image paths for all images you've shared
        # Profile icon
        profile_icon_path = resource_path('assets/images/profile.png')
        profile_icon = QIcon(profile_icon_path)
         # Start icon
        start_icon_path = resource_path('assets/images/start.png')
        start_icon = QIcon(start_icon_path)

        # Add icon
        add_icon_path = resource_path('assets/images/add.png')
        dd_icon = QIcon(add_icon_path)

        # Addons icon
        addons_icon_path = resource_path('assets/images/addons.png')
        addons_icon = QIcon(addons_icon_path)
        # Edit icon
        edit_icon_path = resource_path('assets/images/edit.png')
        edit_icon = QIcon(edit_icon_path)

            # Enabled icon
        enabled_icon_path = resource_path('assets/images/enabled.png')
        enabled_icon = QIcon(enabled_icon_path)

        # Help icon
        help_icon_path = resource_path('assets/images/help.png')
        help_icon = QIcon(help_icon_path)

        # Plugins icon
        plugins_icon_path = resource_path('assets/images/plugins.png')
        plugins_icon = QIcon(plugins_icon_path)

        # Settings icon
        settings_icon_path = resource_path('assets/images/settings.png')

        settings_icon = QIcon(settings_icon_path)

        # Toggle On icon
        toggle_on_icon_path = resource_path('assets/images/toggleon.png')
        toggle_on_icon = QIcon(toggle_on_icon_path)

        # Toggle Off icon
        toggle_off_icon_path = resource_path('assets/images/toggleoff.png')
        toggle_off_icon = QIcon(toggle_off_icon_path)

        # fg.ico (Main Icon)
        main_icon_path = resource_path('assets/images/fg.ico')
        main_icon = QIcon(main_icon_path)

    def init_ui(self):
        """Initialize the main UI, sidebar, and content area."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the main layout for the window
        main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setIconSize(QSize(64, 64))  # Set the icon size
        self.sidebar.setFixedWidth(150)  # Adjust the sidebar width

               # Add sidebar items with icons using resource_path
        self.add_sidebar_item("Profiles", QIcon(resource_path('assets/images/profile.png')))
        self.add_sidebar_item("Addons", QIcon(resource_path('assets/images/addons.png')))
        self.add_sidebar_item("Plugins", QIcon(resource_path('assets/images/plugins.png')))
        self.add_sidebar_item("Help", QIcon(resource_path('assets/images/help.png')))  # Add Help icon here


        self.sidebar.currentRowChanged.connect(self.display_tab)

        # Content area
        self.content_area = QStackedWidget()

        # Initialize the sections for each tab
        self.init_profile_tab()  # Profile Tab with dropdown
        self.init_addons_tab()   # Addons Tab with dropdown
        self.init_plugins_tab()  # Plugins Tab (you can add a dropdown if needed)
        self.init_help_tab()     # Help Tab for displaying help documentation

        # Add tabs to the QStackedWidget
        self.content_area.addWidget(self.profile_tab)  # Index 0
        self.content_area.addWidget(self.addons_tab)   # Index 1
        self.content_area.addWidget(self.plugins_tab)  # Index 2
        self.content_area.addWidget(self.help_tab)     # Index 3 (Help tab)

        # Toggle Button for theme (light/dark) using images
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(QIcon(resource_path('assets/images/toggleoff.png')))
        self.toggle_button.setIconSize(QSize(64, 64))  # Set appropriate size
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(self.settings['theme'] == 'light')
        self.toggle_button.setStyleSheet("background-color: transparent; border: none;")
        self.toggle_button.clicked.connect(self.switch_theme)


        # Sidebar and content layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar)
        sidebar_layout.addWidget(self.toggle_button, alignment=Qt.AlignBottom)

        main_layout.addLayout(sidebar_layout)
        main_layout.addWidget(self.content_area)

        # Set the default view to the Profiles tab
        self.content_area.setCurrentIndex(0)


    def init_profile_tab(self):
        """Initialize the profiles tab with scroll support and an add profile button."""
        self.profile_tab = QWidget()

        profile_scroll_area = QScrollArea(self)
        profile_scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)

        self.profile_layout = QVBoxLayout()
        self.load_profiles()
        scroll_content_layout.addLayout(self.profile_layout)

        profile_scroll_area.setWidget(scroll_content)
        self.profile_tab_layout = QVBoxLayout(self.profile_tab)
        self.profile_tab_layout.addWidget(profile_scroll_area)

        # Add the "Create New Profile" button
        self.add_profile_button = QPushButton(self)
        self.add_profile_button.setIcon(QIcon(resource_path('assets/images/add.png')))
        self.add_profile_button.setIconSize(QSize(40, 40))  # Adjust size as needed
        self.add_profile_button.setFixedSize(120, 40)  # Adjust size as needed
        self.add_profile_button.setStyleSheet("background-color: transparent; border: none;")
        self.add_profile_button.setText(" Add New Profile")
        self.add_profile_button.clicked.connect(self.create_new_profile)



        # Add the button to the layout at the bottom
        self.profile_tab_layout.addWidget(self.add_profile_button, alignment=Qt.AlignBottom)
    def create_new_profile(self):
        """Creates a new profile by copying the default profile and refreshing the profiles list."""
        default_profile_path = os.path.join('assets', 'config', 'default_profile.ini')
        profiles_dir = "./config/boot"

        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        new_profile_name = "new_profile.ini"
        new_profile_path = os.path.join(profiles_dir, new_profile_name)

        try:
            # Copy the default profile to the new profile location
            with open(default_profile_path, 'r') as default_file:
                with open(new_profile_path, 'w') as new_file:
                    new_file.write(default_file.read())

            print(f"Created new profile: {new_profile_name}")

            # Refresh the profiles list
            self.load_profiles()

        except Exception as e:
            print(f"Error creating new profile: {e}")


    def init_addons_tab(self):
        """Initialize the addons tab with scroll support and layout."""
        self.addons_tab = QWidget()

        # Create a dropdown to choose a file
        self.addons_dropdown = QComboBox()
        files = self.get_file_list()

        # Add "Choose file" as the default placeholder
        self.addons_dropdown.addItem("Choose file")
        self.addons_dropdown.addItems(files)  # Add the rest of the files

        self.addons_dropdown.currentIndexChanged.connect(self.set_selected_file)

        # Initialize selected_file_path for safety
        self.selected_file_path = None  # Start with no file selected

        # Create a scroll area for addons
        self.addons_scroll_area = QScrollArea(self)
        self.addons_scroll_area.setWidgetResizable(True)
        self.addons_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.addons_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Create the content inside the scroll area
        scroll_content = QWidget()
        self.addons_layout = QVBoxLayout(scroll_content)  # Initialize the layout here

        # Initially don't display addons
        # The display_addons() function will be called when a file is selected

        # Set the scroll content inside the scroll area
        self.addons_scroll_area.setWidget(scroll_content)

        # Create a layout for the entire addons tab (including dropdown at top)
        layout = QVBoxLayout(self.addons_tab)
        layout.addWidget(self.addons_dropdown)
        layout.addWidget(self.addons_scroll_area)

        # Initially disable the scroll area (until a file is chosen)
        self.addons_scroll_area.setVisible(False)  # Hide until file selection



    def init_plugins_tab(self):
        """Initialize the plugins tab with scroll support."""
        self.plugins_tab = QWidget()
        plugins_scroll_area = QScrollArea(self)
        plugins_scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_content_layout = QVBoxLayout(scroll_content)

        self.display_plugins(scroll_content_layout)

        plugins_scroll_area.setWidget(scroll_content)
        self.plugins_layout = QVBoxLayout(self.plugins_tab)
        self.plugins_layout.addWidget(plugins_scroll_area)

        scroll_content_layout.addStretch()

    def launch_profile(self, profile_name):
        # Path to Ashita-cli executable (just the executable, no profile path)
        ashita_cli_path = os.path.join(os.path.abspath("."), "Ashita-cli.exe")

        # Ensure the profile name ends with .ini
        if not profile_name.endswith(".ini"):
            profile_name += ".ini"

        # Command to launch Ashita-cli with the profile (just the profile name)
        game_launch_command = [ashita_cli_path, profile_name]  # Only pass the profile name, no path

        # Check if Ashita-cli exists
        if not os.path.exists(ashita_cli_path):
            print(f"Ashita-cli.exe not found at {ashita_cli_path}")
            return

        # Check if profile exists
        profile_path = os.path.join(os.path.abspath("."), "config", "boot", profile_name)
        if not os.path.exists(profile_path):
            print(f"Profile {profile_name} not found at {profile_path}")
            return

        try:
            # Use subprocess to launch Ashita-cli.exe with the profile (in a new console window)
            subprocess.Popen(game_launch_command, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Launching Ashita with profile: {profile_name}")
        except Exception as e:
            print(f"Failed to launch Ashita with profile {profile_name}: {e}")
    def check_and_copy_default_config(self):
        """Check if Fantasy_Gateway.txt exists in the scripts folder, if not copy it from assets/config/"""
        scripts_folder = './scripts'
        config_path = os.path.join(scripts_folder, 'Fantasy_Gateway.txt')

        # Check if the Fantasy_Gateway.txt exists
        if not os.path.exists(config_path):
            print("Fantasy_Gateway.txt not found in scripts folder. Copying from assets/config.")
            source_config = './assets/config/Fantasy_Gateway.txt'

            # Ensure the scripts folder exists
            if not os.path.exists(scripts_folder):
                os.makedirs(scripts_folder)

            try:
                # Copy the default config from assets/config/ to scripts/
                shutil.copy(source_config, config_path)
                print(f"Copied Fantasy_Gateway.txt to {scripts_folder}.")
            except Exception as e:
                print(f"Error copying Fantasy_Gateway.txt: {e}")
        else:
            print("Fantasy_Gateway.txt already exists in the scripts folder.")
    def set_selected_file(self):
        """Set the selected file path from the dropdown and update the checkboxes."""
        selected_file = self.addons_dropdown.currentText()

        # If no file is selected or the default "Choose file" is selected, do nothing
        if not selected_file or selected_file == "Choose file":
            print("No valid file selected.")
            self.addons_scroll_area.setVisible(False)
            return

        # Add .txt extension if missing
        new_file_path = os.path.join('./scripts', selected_file)
        if not selected_file.endswith('.txt'):
            new_file_path += '.txt'

        # If the selected file path is already the current one, don't reload
        if self.selected_file_path == new_file_path:
            print(f"File already selected: {self.selected_file_path}")
            return

        # Update the file path and reload the addons
        self.selected_file_path = new_file_path
        print(f"Selected file path: {self.selected_file_path}")

        # Clear the current addons layout before displaying the new ones
        self.clear_layout(self.addons_layout)

        # Load the selected file and display the addons
        self.load_addons_plugins_from_file()
        self.display_addons(self.addons_layout)  # Use the unified function

        # Show the scroll area after a valid file is selected
        self.addons_scroll_area.setVisible(True)
    

    
    

    def init_help_tab(self):
        """Initialize the Help tab with help documentation."""
        self.help_tab = QWidget()

        # Initialize the layout for the help tab
        help_layout = QVBoxLayout(self.help_tab)
    
        # Create a scroll area for the help content
        scroll_area = QScrollArea(self.help_tab)
        scroll_area.setWidgetResizable(True)

        # Help content widget
        help_content_widget = QWidget()
        help_content_layout = QVBoxLayout(help_content_widget)
    
        # Help content with custom font sizes
        help_content = QLabel("""
            <h2 style="font-size: 20px;">Fantasy Gateway Help</h2>
            <p style="font-size: 14px;">Welcome to Fantasy Gateway, your all-in-one launcher management tool.</p>
        
            <h3 style="font-size: 18px;">Profiles</h3>
            <p style="font-size: 14px;">Manage game profiles here. You can view profile details, launch, and edit profiles.</p>

            <h3>Addons</h3>
            <p style="font-size: 14px;">
            This section allows you to manage game addons. You can load or unload addons by selecting a file from the dropdown and checking the respective checkboxes.
            <a href="https://docsv3.ashitaxi.com/addons">https://docsv3.ashitaxi.com/addons</a>
            </p>

            <h3 style="font-size: 18px;">Plugins</h3>
            <p style="font-size: 14px;">Manage your game plugins here. You can load or unload plugins using the checkboxes provided in this section.
            <a href="https://docsv3.ashitaxi.com/addons">https://docsv3.ashitaxi.com/plugins</a>
            </p>

            <h3 style="font-size: 18px;">Settings</h3>
            <p style="font-size: 14px;">Use the toggle at the bottom left to switch between dark and light themes.</p>

            <h3 style="font-size: 18px;">Help</h3>
            <p style="font-size: 14px;">You are currently viewing the Help section. For more detailed documentation, refer to our official website or contact support.</p>

            <h3 style="font-size: 18px;">Configuration File: default.txt</h3>
            <p style="font-size: 14px;">The <b>default.txt</b> file stores your addon and plugin configurations. Make sure that this file contains the following sections to allow proper functionality:</p>
            <ul style="font-size: 14px;">
                <li><b>Plugin Section</b>: Used for loading plugins. It should have the following lines:</li>
                <pre style="font-size: 14px;">
                # Plugin Section Start
                # Plugin Section End
                </pre>

                <li><b>Addon Section</b>: Used for loading addons. It should have the following lines:</li>
                <pre style="font-size: 14px;">
                # Addon Section Start
                # Addon Section End
                </pre>
            </ul>
            <p style="font-size: 14px;">If the <b>default.txt</b> file is missing, the system will automatically create one with these required sections.</p>

            <h3 style="font-size: 18px;">Edit Profile Settings</h3>
            <p style="font-size: 14px;">In the Edit Profile tab, you can adjust various profile settings. Below is a detailed explanation of each setting:</p>

            <ul style="font-size: 14px;">
                <li><b>Resolution Width & Height</b>: Sets the in-game resolution. Both width and height must be configured for optimal display. These settings correspond to fields <b>0001</b> and <b>0002</b> in the configuration file.</li>

                <li><b>Background Resolution</b>: This sets the background rendering resolution, and it's reflected in fields <b>0003</b> and <b>0004</b> in the config. A higher background resolution improves quality but may reduce performance.</li>

                <li><b>Fullscreen Mode</b>: Enable or disable fullscreen mode for the game. Toggle this setting depending on whether you want to play in windowed mode or fullscreen.</li>

                <li><b>Gamepad Allow Background Input</b>: This option allows the gamepad to work even when the game window is not in focus. Useful if you're multi-tasking while playing.</li>

                <li><b>Mouse Unhook</b>: Determines whether the mouse remains "hooked" to the game window. If you disable this, you can move your cursor outside the game while it is running in windowed mode.</li>
                                
                <li><b>Commands on Launch</b>: Here, you can define specific commands that will be run when the profile is launched. For example, --server homepointxi.com --user username --password password. </li>
            </ul>

            <h3 style="font-size: 18px;">Additional Information</h3>
            <p style="font-size: 14px;">Make sure to configure each setting correctly to ensure a smooth gaming experience. If you encounter any issues, feel free to consult our support or visit the official documentation.</p>
        """)

        help_content.setWordWrap(True)
        help_content_layout.addWidget(help_content)
        help_content.setOpenExternalLinks(True)  # This allows clicking on the link to open it in a browser
        # Set the scroll area widget
        scroll_area.setWidget(help_content_widget)
    
        # Add the scroll area to the help layout
        help_layout.addWidget(scroll_area)



    def load_profiles(self):
        """Load profiles and display them in the Profiles tab."""
        profiles_dir = "./config/boot"
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)

        # Clear previous profiles
        while self.profile_layout.count():
            widget = self.profile_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

        # Load and display profiles
        for profile in os.listdir(profiles_dir):
            if profile.endswith(".ini"):
                profile_name = profile.replace(".ini", "")
                profile_info = self.get_profile_info(os.path.join(profiles_dir, profile))
                self.create_profile_widget(profile_name, profile_info)

    def load_files_from_scripts_folder(self, dropdown):
        """Load .txt files from the scripts folder and populate the dropdown."""
        scripts_folder = './scripts'
        if os.path.exists(scripts_folder):
            txt_files = [f.replace('.txt', '') for f in os.listdir(scripts_folder) if f.endswith('.txt')]
            dropdown.addItems(txt_files)
        else:
            print("Scripts folder not found.")

    def save_changes_to_file(self):
        """Save the current state of addons to the selected file."""
        # Ensure a file is selected from the dropdown
        selected_file = self.addons_dropdown.currentText()  # Make sure your dropdown is named 'addons_dropdown'
    
        if not selected_file:
            print("No file selected from the dropdown.")
            return  # Exit if no file is selected
    
        file_path = os.path.join('./scripts', selected_file + '.txt')  # Proper file path creation

        try:
            with open(file_path, 'w') as f:
                # Write the state of addons to the file
                for addon, enabled in self.manager.addons.items():  # Assuming 'self.manager.addons' holds the addon states
                    state = 'enabled' if enabled else 'disabled'
                    f.write(f"{addon}: {state}\n")

            print(f"Saved addon states to {file_path}")
        except Exception as e:
            print(f"Failed to save addon states: {e}")


        print(f"Saved addon states to {file_path}")
    def get_file_list(self):
        """Fetches a list of .txt files from the scripts folder."""
        scripts_folder = './scripts'
    
        # Ensure the scripts folder exists
        if not os.path.exists(scripts_folder):
            return []

        # List all .txt files in the directory
        txt_files = [f for f in os.listdir(scripts_folder) if f.endswith('.txt')]
    
        return txt_files
    def open_profile_editor(self, profile_name, profile_path):
        """Opens the profile editor dialog for the given profile."""
        # Assuming ProfileEditor is a dialog class you have or will create
        editor = ProfileEditor(profile_name, profile_path, self)  # Create the profile editor dialog
        editor.exec_()  # Show the dialog

    def get_profile_info(self, profile_path):
        """Get profile information (like resolution) from the profile file."""
        config = configparser.ConfigParser()
        config.read(profile_path)

        # Extract resolution info
        width = config.get("ffxi.registry", "0001", fallback="Unknown")
        height = config.get("ffxi.registry", "0002", fallback="Unknown")
        return {"resolution": f"{width}x{height}"}

    def create_profile_widget(self, profile_name, profile_info):
        """Creates a custom widget for each profile with name, info, and buttons."""
        profile_widget = QWidget()
        profile_layout = QHBoxLayout(profile_widget)

        # Profile info section with modified font sizes
        profile_label = QLabel(f"""
            <b style="font-size: 16px;">{profile_name}</b><br>
            <span style="font-size: 12px;">Resolution: {profile_info['resolution']}</span>
        """)

        # Start button with icon and transparent background
        start_button = QPushButton()
        start_button.setIcon(QIcon("assets/images/start.png"))
        start_button.setIconSize(QSize(40, 40))  # Adjust size if needed
        start_button.setFixedSize(40, 40)
        start_button.setStyleSheet("background-color: transparent; border: none;")
        start_button.clicked.connect(lambda: self.launch_profile(profile_name))

        # Edit button with icon and transparent background
        edit_button = QPushButton()
        edit_button.setIcon(QIcon("assets/images/edit.png"))
        edit_button.setIconSize(QSize(40, 40))
        edit_button.setFixedSize(40, 40)
        edit_button.setStyleSheet("background-color: transparent; border: none;")
        edit_button.clicked.connect(lambda: self.open_profile_editor(profile_name, f"./config/boot/{profile_name}.ini"))

        # Set a fixed size for the profile widget
        profile_widget.setFixedHeight(60)

        # Add elements to the layout
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(start_button)
        profile_layout.addWidget(edit_button)

        # Add profile widget to the main profile layout
        self.profile_layout.addWidget(profile_widget)

                
    def display_tab(self, index):
        current_index = self.content_area.currentIndex()

        if current_index == 1 and index != 1:  # Leaving Addons tab
            self.update_addon_plugin_file(is_addon=True)  # Save Addon states
        elif current_index == 2 and index != 2:  # Leaving Plugins tab
            self.update_addon_plugin_file(is_addon=False)  # Save Plugin states

        # Switch tabs
        self.content_area.setCurrentIndex(index)

        # Reload the data for the new tab
        if index == 1:  # Addons tab
            self.load_addons_plugins_from_file()
            self.update_addon_checkboxes()
        elif index == 2:  # Plugins tab
            self.load_addons_plugins_from_file()
            self.update_plugin_checkboxes()



    def display_items(self, items, layout, state_update_function):
        """Generic function to display addons or plugins."""
        self.clear_layout(layout)
        for item, enabled in items.items():
            checkbox = QCheckBox(item)
            checkbox.setChecked(enabled)
            # Fix the partial binding issue using lambda
            checkbox.stateChanged.connect(lambda state, item=item: state_update_function(item, state))
            layout.addWidget(checkbox)
        layout.addStretch()


    def display_addons(self, layout):
        """Create and display checkboxes for addons in rows using a grid layout."""
        # Clear the layout to prevent duplicates
        self.clear_layout(layout)  # Make sure this is called first to remove any existing widgets

        addons = self.manager.get_addons()

        if not addons:
            print("No addons found or failed to load addons!")
            return

        # Create a grid layout for the checkboxes
        grid_layout = QGridLayout()

        # Set how many columns you want in a row
        columns = 3  # Adjust this based on preference

        row = 0
        col = 0

        for i, (addon, enabled) in enumerate(addons.items()):
            checkbox = QCheckBox(addon)
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(partial(self.update_addon_state, addon))  # Use partial to bind correctly
            checkbox.setStyleSheet("font-size: 16px;")  # Increase font size for readability

            # Add the checkbox to the grid layout
            grid_layout.addWidget(checkbox, row, col)

            # Move to the next column
            col += 1

            # If we have reached the number of columns, move to the next row
            if col >= columns:
                col = 0
                row += 1

        # Add the grid layout to the main layout
        layout.addLayout(grid_layout)

    

    def display_plugins(self, layout):
        """Displays plugins in the layout."""
        plugins = self.manager.get_plugins()
        self.display_items(plugins, layout, self.update_plugin_state)

    def clear_layout(self, layout):
        """Clears all widgets from the layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():  # If there are nested layouts
                self.clear_layout(child.layout())


    def update_plugin_state(self, plugin, state):
        """Update the state of a plugin and save changes to the file."""
        is_enabled = state == Qt.Checked
        self.manager.plugins[plugin] = is_enabled
        self.update_addon_plugin_file(is_addon=False)  # Update the file when the state changes

    def update_addon_state(self, addon, state):
        """Update the state of an addon and save changes to the file."""
        is_enabled = state == Qt.Checked
        self.manager.addons[addon] = is_enabled
        self.update_addon_plugin_file(is_addon=True)  # Update the file when the state changes
    def update_plugin_checkboxes(self):
        """Updates the checkboxes in the Plugins tab to reflect the current state."""
        # Clear the existing layout before updating the checkboxes
        self.clear_layout(self.plugins_layout)  # Clear old widgets
    
        # Display the updated plugin checkboxes
        plugins = self.manager.get_plugins()
    
        if not plugins:
            print("No plugins found or failed to load plugins!")
            return

        # Create a grid layout for the checkboxes
        grid_layout = QGridLayout()

        # Set how many columns you want in a row
        columns = 3  # Change this value to have more or fewer checkboxes per row

        row = 0
        col = 0

        for i, (plugin, enabled) in enumerate(plugins.items()):
            checkbox = QCheckBox(plugin)
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(partial(self.update_plugin_state, plugin))

            checkbox.setStyleSheet("font-size: 16px;")  # Increase font size for readability
    
            # Add the checkbox to the grid layout
            grid_layout.addWidget(checkbox, row, col)

            # Move to the next column
            col += 1

            # If we have reached the number of columns, move to the next row
            if col >= columns:
                col = 0
                row += 1

        # Add the grid layout to the main layout
        self.plugins_layout.addLayout(grid_layout)


    def update_addon_checkboxes(self):
        """Updates the checkboxes in the Addons tab to reflect the current state."""
        # Clear the existing layout before updating the checkboxes
        self.clear_layout(self.addons_layout)  # Clear old widgets
    
        # Display the updated addon checkboxes
        addons = self.manager.get_addons()
    
        if not addons:
            print("No addons found or failed to load addons!")
            return

        # Create a grid layout for the checkboxes
        grid_layout = QGridLayout()

        # Set how many columns you want in a row
        columns = 3  # Change this value to have more or fewer checkboxes per row

        row = 0
        col = 0

        for i, (addon, enabled) in enumerate(addons.items()):
            checkbox = QCheckBox(addon)
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(partial(self.update_addon_state, addon))
            checkbox.setStyleSheet("font-size: 16px;")  # Increase font size for readability
    
            # Add the checkbox to the grid layout
            grid_layout.addWidget(checkbox, row, col)

            # Move to the next column
            col += 1

            # If we have reached the number of columns, move to the next row
            if col >= columns:
                col = 0
                row += 1

        # Add the grid layout to the main layout
        self.addons_layout.addLayout(grid_layout)
    def load_addons_plugins_from_file(self):
        """Reads the file and updates the addon/plugin states based on the file's content."""
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            print("No file selected. Please choose a file from the dropdown.")
            return

        file_path = os.path.normpath(self.selected_file_path)
        print(f"Loading file: {file_path}")

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return

        # Only reset addons or plugins that are explicitly mentioned in the file
        in_addon_section = False
        in_plugin_section = False

        for line in lines:
            line = line.strip()

            if "# Addon Section Start" in line:
                in_addon_section = True
                in_plugin_section = False
                continue
            elif "# Addon Section End" in line:
                in_addon_section = False
                continue

            if "# Plugin Section Start" in line:
                in_plugin_section = True
                in_addon_section = False
                continue
            elif "# Plugin Section End" in line:
                in_plugin_section = False
                continue

            if in_addon_section and line.startswith("/addon load"):
                addon_name = line.split(" ")[-1]
                if addon_name in self.manager.addons:
                    self.manager.addons[addon_name] = True

            elif in_plugin_section and line.startswith("/load"):
                plugin_name = line.split(" ")[-1].replace('.dll', '')  # Ensure the plugin is loaded without .dll
                if plugin_name in self.manager.plugins:
                    self.manager.plugins[plugin_name] = True

        # After parsing the file, update the checkboxes in the UI
        self.update_addon_checkboxes()
        self.update_plugin_checkboxes()
        print("Updated addon and plugin checkboxes")
    def update_addon_plugin_file(self, is_addon=True):
        """Updates the configuration file with the enabled addons/plugins."""
        if not self.selected_file_path:
            print("No file selected to save changes.")
            return

        file_path = os.path.normpath(self.selected_file_path)

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return

        if is_addon:
            start_marker = "# Addon Section Start"
            end_marker = "# Addon Section End"
            updated_items = [f"/addon load {addon}\n" for addon, enabled in self.manager.addons.items() if enabled]
        else:
            start_marker = "# Plugin Section Start"
            end_marker = "# Plugin Section End"
            updated_items = [f"/load {plugin}\n" for plugin, enabled in self.manager.plugins.items() if enabled]

        try:
            start_index = next(i for i, line in enumerate(lines) if start_marker in line)
            end_index = next(i for i, line in enumerate(lines) if end_marker in line)
            lines = lines[:start_index + 1] + updated_items + lines[end_index:]
        except StopIteration:
            print(f"Error: Could not find section markers in {file_path}.")
            return

        try:
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print(f"File {file_path} updated successfully.")
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")



    
    def add_sidebar_item(self, label_text, icon_path):
        """Adds a labeled item with an icon to the sidebar."""
        item = QListWidgetItem(QIcon(icon_path), label_text)
        item.setSizeHint(QSize(140, 80))
        self.sidebar.addItem(item)

    def set_selected_file(self):
        """Set the selected file path from the dropdown and update the checkboxes."""
        selected_file = self.addons_dropdown.currentText()

        # If no file is selected or the default "Choose file" is selected, do nothing
        if not selected_file or selected_file == "Choose file":
            print("No valid file selected.")
            self.addons_scroll_area.setVisible(False)  # Hide the scroll area if no file is selected
            return

        # Add .txt extension if missing
        new_file_path = os.path.join('./scripts', selected_file)
        if not selected_file.endswith('.txt'):
            new_file_path += '.txt'

        # If the selected file path is already the current one, don't reload
        if self.selected_file_path == new_file_path:
            print(f"File already selected: {self.selected_file_path}")
            return

        # Update the file path
        self.selected_file_path = new_file_path
        print(f"Selected file path: {self.selected_file_path}")

        # Clear the current addons layout before displaying the new ones
        self.clear_layout(self.addons_layout)

        # Load the selected file and display the addons
        self.load_addons_plugins_from_file()  # Load the addon states from the file
        self.display_addons(self.addons_layout)  # Display the addons in the layout

        # Show the scroll area after a valid file is selected
        self.addons_scroll_area.setVisible(True)  # Show the addons scroll area






    def switch_theme(self):
        """Switch between dark and light themes."""
        if self.toggle_button.isChecked():
            self.toggle_button.setIcon(QIcon("assets/images/toggleon.png"))
            self.settings['theme'] = 'light'
            self.apply_light_theme()
        else:
            self.toggle_button.setIcon(QIcon("assets/images/toggleoff.png"))
            self.settings['theme'] = 'dark'
            self.apply_dark_theme()
        save_settings(self.settings)

    def apply_dark_theme(self, window=None):
        """Applies a dark theme to the entire GUI."""
        target_window = window if window else self  # Apply theme to the given window or self
        target_window.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #ff4500;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QCheckBox {
                color: white;
            }
            QListWidget {
                background-color: #3a3a3a;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #5a5a5a;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: white;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #ff4500;
                color: white;
            }
        """)

    def apply_light_theme(self, window=None):
        """Applies a light theme to the entire GUI."""
        target_window = window if window else self  # Apply theme to the given window or self
        target_window.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #f0f0f0;
                color: black;
            }
            QLabel {
                color: black;
            }
            QLineEdit {
                background-color: #ffffff;
                color: black;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QCheckBox {
                color: black;
            }
            QListWidget {
                background-color: #ffffff;
                color: black;
            }
            QListWidget::item:selected {
                background-color: #dddddd;
            }
            QTabWidget::pane {
                border: 1px solid #dddddd;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: black;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background-color: #0078d7;
                color: white;
            }
        """)



class ProfileEditor(QDialog):
    """Profile Editor Dialog with Scroll Area for Advanced Settings."""

    def __init__(self, profile_name, profile_path, parent=None, current_theme="dark"):
        super(ProfileEditor, self).__init__(parent)
        self.profile_name = profile_name
        self.profile_path = profile_path
        self.current_theme = current_theme  # Store the current theme

        # Ashita Boot Settings
        self.ashita_boot_settings_map = {
            "file": {"label": "Bootloader File", "type": "file_browser", "default": ".\\bootloader\\xiloader.exe"},
            "command": {"label": "Server Command", "type": "input", "default": "--server homepointxi.com"},
            #"gamemodule": {"label": "Game Module", "type": "input", "default": "ffximain.dll"},
            "script": {"label": "Startup Script", "type": "input", "default": "default.txt"},
            "args": {"label": "Additional Arguments", "type": "input", "default": ""}
        }

        # FFXI Registry Settings
        self.settings_map = {
            #"sandbox": {"label": "Enable Sandbox Mode", "type": "checkbox", "default": "0"},
            "0000": {"label": "Mip Mapping", "type": "dropdown", "options": ["Off", "Low", "High"], "default": "6"},
            "0001": {"label": "Window Resolution Width", "type": "input", "default": "1920"},
            "0002": {"label": "Window Resolution Height", "type": "input", "default": "1080"},
            "0003": {"label": "Background Resolution Width", "type": "input", "default": "4096"},
            "0004": {"label": "Background Resolution Height", "type": "input", "default": "4096"},
            "0007": {"label": "Sound Enabled", "type": "checkbox", "default": "1"},
            "0011": {"label": "Environment Animations", "type": "dropdown", "options": ["Off", "Normal", "Smooth"], "default": "1"},
            "0017": {"label": "Bump Mapping", "type": "checkbox", "default": "1"},
            "0018": {"label": "Texture Compression", "type": "dropdown", "options": ["High", "Low", "Uncompressed"], "default": "2"},
            "0019": {"label": "Texture Compression (Uncompressed)", "type": "checkbox", "default": "1"},
            "0021": {"label": "Hardware Mouse", "type": "checkbox", "default": "1"},
            "0022": {"label": "Show Opening Movie", "type": "checkbox", "default": "0"},
            "0023": {"label": "Simplified Character Creation Visuals", "type": "checkbox", "default": "0"},
            "0029": {"label": "Maximum Number of Sounds", "type": "input", "default": "20"},
            "0034": {"label": "Windowed Mode", "type": "dropdown", "options": ["Fullscreen", "Windowed", "Fullscreen Windowed", "Borderless Windowed"], "default": "1"},
            "0035": {"label": "Sound Always On", "type": "checkbox", "default": "1"},
            "0036": {"label": "Font Compression", "type": "dropdown", "options": ["Compressed", "Uncompressed", "High Quality"], "default": "2"},
            "0037": {"label": "Menu Resolution Width", "type": "input", "default": "1920"},
            "0038": {"label": "Menu Resolution Height", "type": "input", "default": "1080"},
            "0040": {"label": "Graphics Stabilization", "type": "checkbox", "default": "0"},
            "0043": {"label": "Screenshot In Screen Resolution", "type": "checkbox", "default": "1"},
            "0044": {"label": "Maintain Window Aspect Ratio", "type": "checkbox", "default": "1"}
        }

        self.setWindowTitle(f"Edit Profile: {profile_name}")
        self.setGeometry(200, 200, 400, 600)

        # Main layout
        layout = QVBoxLayout(self)

        # Profile Name Field
        self.name_input = QLineEdit(self)
        self.name_input.setText(self.profile_name)
        layout.addWidget(QLabel("Profile Name:"))
        layout.addWidget(self.name_input)

        # Scroll area for settings
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(10)

        # Create all the settings here
        self.create_config_form(scroll_layout)

        # Add the scroll widget to the scroll area
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_profile)
        layout.addWidget(self.save_button)

        # Load existing profile settings
        try:
            profile_data = load_profile(self.profile_path)
            self.load_profile_data(profile_data)  # Load data into the fields
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.close()
            return

        # Apply the current theme
        self.apply_theme()
    
    
    def create_config_form(self, layout):
        """Creates the form layout for all settings."""
        form_layout = QFormLayout()

        # Loop through Ashita Boot settings and create fields dynamically
        for key, setting in self.ashita_boot_settings_map.items():
            label = QLabel(setting['label'])
            if setting["type"] == "input":
                input_field = QLineEdit(self)
                input_field.setText(setting.get("default", ""))
                form_layout.addRow(label, input_field)
                setattr(self, f"{key}_input", input_field)

            elif setting["type"] == "file_browser":
                input_field = QLineEdit(self)
                browse_button = QPushButton("Browse")
                browse_button.clicked.connect(partial(self.browse_file, input_field))  # Use partial to create a closure
                input_field.setText(setting.get("default", ""))
                file_layout = QHBoxLayout()
                file_layout.addWidget(input_field)
                file_layout.addWidget(browse_button)
                form_layout.addRow(label, file_layout)
                setattr(self, f"{key}_input", input_field)

        # Loop through FFXI Registry settings and create fields dynamically, excluding sandbox
        for key, setting in self.settings_map.items():
            if key == "sandbox":
                continue  # Skip sandbox as it's manually handled below

            label = QLabel(setting['label'])
            if setting["type"] == "input":
                input_field = QLineEdit(self)
                input_field.setText(setting.get("default", ""))
                form_layout.addRow(label, input_field)
                setattr(self, f"{key}_input", input_field)  # Correct attribute assignment here
            elif setting["type"] == "checkbox":
                checkbox = QCheckBox(self)
                form_layout.addRow(label, checkbox)
                setattr(self, f"{key}_checkbox", checkbox)

        # Sandbox mode settings (only show if sandbox is enabled)
        self.sandbox_checkbox = QCheckBox("Enable Sandbox Mode", self)
        self.sandbox_checkbox.setChecked(False)
        self.sandbox_checkbox.stateChanged.connect(self.toggle_sandbox_settings)
        form_layout.addRow(self.sandbox_checkbox)

        # Add input fields for the sandbox paths with directory choosers
        self.common_path_input = QLineEdit(self)
        self.common_browse_button = QPushButton("Browse")
        self.common_browse_button.clicked.connect(partial(self.browse_directory, self.common_path_input))
    
        self.pol_path_input = QLineEdit(self)
        self.pol_browse_button = QPushButton("Browse")
        self.pol_browse_button.clicked.connect(partial(self.browse_directory, self.pol_path_input))

        self.ffxi_path_input = QLineEdit(self)
        self.ffxi_browse_button = QPushButton("Browse")
        self.ffxi_browse_button.clicked.connect(partial(self.browse_directory, self.ffxi_path_input))

        # Add layout for common directory
        common_layout = QHBoxLayout()
        common_layout.addWidget(self.common_path_input)
        common_layout.addWidget(self.common_browse_button)
        form_layout.addRow(QLabel("Common Directory Path:"), common_layout)

        # Add layout for POL directory
        pol_layout = QHBoxLayout()
        pol_layout.addWidget(self.pol_path_input)
        pol_layout.addWidget(self.pol_browse_button)
        form_layout.addRow(QLabel("POL Directory Path:"), pol_layout)

        # Add layout for FFXI directory
        ffxi_layout = QHBoxLayout()
        ffxi_layout.addWidget(self.ffxi_path_input)
        ffxi_layout.addWidget(self.ffxi_browse_button)
        form_layout.addRow(QLabel("FFXI Directory Path:"), ffxi_layout)

        # Hide these fields by default
        self.common_path_input.hide()
        self.common_browse_button.hide()
        self.pol_path_input.hide()
        self.pol_browse_button.hide()
        self.ffxi_path_input.hide()
        self.ffxi_browse_button.hide()

        # Add form layout to the main scroll layout
        layout.addLayout(form_layout)
    
    def toggle_sandbox_settings(self, state):
        """Toggles the sandbox-specific settings when the sandbox checkbox is checked."""
        if state == Qt.Checked:
            # Show sandbox paths when sandbox mode is enabled
            self.common_path_input.show()
            self.common_browse_button.show()
            self.pol_path_input.show()
            self.pol_browse_button.show()
            self.ffxi_path_input.show()
            self.ffxi_browse_button.show()
        else:
            # Hide sandbox paths when sandbox mode is disabled
            self.common_path_input.hide()
            self.common_browse_button.hide()
            self.pol_path_input.hide()
            self.pol_browse_button.hide()
            self.ffxi_path_input.hide()
            self.ffxi_browse_button.hide()
    
    def browse_directory(self, input_field):
        """Opens a file dialog to select the directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if directory:
            input_field.setText(directory)
    
    
    

    def browse_file(self, input_field):
        """Opens a file dialog to select the file for the given input."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Executables (*.exe);;All Files (*)")
        if file_path:
            input_field.setText(file_path)

    def load_profile_data(self, profile_data):
        """Loads existing profile data into the editor fields."""
        config = configparser.ConfigParser()
        config.read(self.profile_path)

        # Load Ashita Boot settings
        if 'ashita.boot' in config:
            self.file_input.setText(config['ashita.boot'].get('file', self.ashita_boot_settings_map['file'].get('default')))
            self.command_input.setText(config['ashita.boot'].get('command', self.ashita_boot_settings_map['command'].get('default')))
            self.script_input.setText(config['ashita.boot'].get('script', self.ashita_boot_settings_map['script'].get('default')))

        # Load Ashita Plugins (Sandbox Mode)
        if 'ashita.polplugins' in config:
            self.sandbox_checkbox.setChecked(config['ashita.polplugins'].get('sandbox', '0') == '1')

        # Load FFXI Registry settings
        if 'ffxi.registry' in config:
            for key, setting in self.settings_map.items():
                field_type = setting['type']
                if field_type == "input":
                    input_field = getattr(self, f"{key}_input", None)
                    if input_field:
                        input_field.setText(config['ffxi.registry'].get(key, setting.get("default")))
                elif field_type == "checkbox":
                    checkbox_field = getattr(self, f"{key}_checkbox", None)
                    if checkbox_field:
                        checkbox_field.setChecked(config['ffxi.registry'].get(key, '0') == '1')

    def save_changes_to_file(self):
        """Save the current state of addons and plugins to the selected file."""
        selected_file = self.addons_dropdown.currentText() + '.txt'
        file_path = os.path.join('./scripts', selected_file)

        # Verify that the file path is correct by printing it
        print(f"Saving to: {file_path}")

        with open(file_path, 'w') as f:
            # Save enabled addons
            for addon, enabled in self.manager.addons.items():
                if enabled:
                    f.write(f'addon:{addon}\n')  # Write enabled addons to the file

            # Save enabled plugins
            for plugin, enabled in self.manager.plugins.items():
                if enabled:
                    f.write(f'plugin:{plugin}\n')  # Write enabled plugins to the file

        print(f"Changes saved to {file_path}.")


    def save_profile(self):
        """Saves the edited profile settings."""
        # Load the current .ini file content
        config = configparser.ConfigParser()  # Make sure 'config' is declared here
        config.read(self.profile_path)  # 'self' refers to the current object
        new_profile_name = self.name_input.text().strip()

        # Ensure the profile name is not empty
        if not new_profile_name:
            QMessageBox.warning(self, "Error", "Profile name cannot be empty.")
            return

        # Rename the profile file if the name has changed
        if new_profile_name != self.profile_name:
            new_profile_path = os.path.join('./config/boot', f"{new_profile_name}.ini")
            try:
                os.rename(self.profile_path, new_profile_path)
                self.profile_path = new_profile_path  # Update the profile path
                self.profile_name = new_profile_name  # Update the profile name
                QMessageBox.information(self, "Success", f"Profile renamed to {new_profile_name}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename profile: {e}")
                return

        # Update settings for Ashita Boot section
        if 'ashita.boot' not in config:
            config.add_section('ashita.boot')

        config['ashita.boot']['file'] = self.file_input.text()
        config['ashita.boot']['command'] = self.command_input.text()
        config['ashita.boot']['script'] = self.script_input.text()

        # Update settings for Ashita Plugins section
        if 'ashita.polplugins' not in config:
            config.add_section('ashita.polplugins')

        # Save sandbox checkbox state
        config['ashita.polplugins']['sandbox'] = '1' if self.sandbox_checkbox.isChecked() else '0'

        # Update settings for FFXI Registry section
        if 'ffxi.registry' not in config:
            config.add_section('ffxi.registry')

        for key, setting in self.settings_map.items():
            field_type = setting['type']
            if field_type == "input":
                input_field = getattr(self, f"{key}_input", None)
                if input_field:
                    config['ffxi.registry'][key] = input_field.text()
            elif field_type == "checkbox":
                checkbox_field = getattr(self, f"{key}_checkbox", None)
                if checkbox_field:
                    config['ffxi.registry'][key] = '1' if checkbox_field.isChecked() else '0'

        # Save sandbox-specific settings if sandbox mode is enabled
        if self.sandbox_checkbox.isChecked():
            sandbox_config_path = "./config/sandbox/sandbox.ini"
            sandbox_config = configparser.ConfigParser()
            sandbox_config.read(sandbox_config_path)

            # Ensure [sandbox.paths] section exists
            if 'sandbox.paths' not in sandbox_config:
                sandbox_config.add_section('sandbox.paths')

            # Update the paths with the directory values
            sandbox_config['sandbox.paths']['common'] = self.common_path_input.text()
            sandbox_config['sandbox.paths']['pol'] = self.pol_path_input.text()
            sandbox_config['sandbox.paths']['ffxi'] = self.ffxi_path_input.text()

            # Save sandbox.ini file
            with open(sandbox_config_path, 'w') as sandbox_configfile:
                sandbox_config.write(sandbox_configfile)

        # Finally, save the updated config back to the profile .ini file
        with open(self.profile_path, 'w') as configfile:
            config.write(configfile)
        
        if self.parent():
            self.parent().load_profiles()


        QMessageBox.information(self, "Success", "Profile saved successfully!")
        self.close()
    def collect_profile_data(self):
        """Collects the profile data from the input fields and returns a dictionary."""
        # This function should gather all the updated data from your input fields
        profile_data = {}
        # Loop over your settings and collect the updated values
        # Example:
        profile_data['0001'] = self.settings_map['0001']['widget'].text()  # Get value from the input
        # Do this for all other settings...

        return profile_data

    def apply_theme(self):
        """Applies the current theme (light or dark) to the profile editor."""
        if self.current_theme == "dark":
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        """Applies the dark theme to the Profile Editor."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
            }
            QPushButton {
                background-color: #ff4500;
                color: white;
                border-radius: 5px;
            }
            QCheckBox {
                color: white;
            }
        """)

    def apply_light_theme(self):
        """Applies the light theme to the Profile Editor."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                color: black;
            }
            QLabel {
                color: black;
            }
            QLineEdit {
                background-color: #ffffff;
                color: black;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
            }
            QCheckBox {
                color: black;
            }
        """)