import os
import json
from PyQt5.QtWidgets import QCheckBox

class AddonPluginManager:
    def __init__(self, addon_folder, plugin_folder, config_file):
        self.addon_folder = addon_folder
        self.plugin_folder = plugin_folder
        self.config_file = config_file
        self.addons = {}
        self.plugins = {}

    def load_config(self):
        """Load the enabled/disabled state of addons and plugins from a config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.addons = config_data.get('addons', {})
                    self.plugins = config_data.get('plugins', {})
            else:
                # If no config file, initialize with empty data
                self.addons = {}
                self.plugins = {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Failed to load config file: {e}")
            self.addons = {}
            self.plugins = {}

    def save_config(self):
        """Save the enabled/disabled state of addons and plugins to a config file."""
        try:
            config_data = {
                'addons': self.addons,
                'plugins': self.plugins
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
        except OSError as e:
            print(f"Failed to save config file: {e}")

    def scan_addons(self):
        """Scan the addon folder and update the addon list."""
        if os.path.exists(self.addon_folder):
            addon_dirs = [d for d in os.listdir(self.addon_folder) if os.path.isdir(os.path.join(self.addon_folder, d))]
            for addon in addon_dirs:
                if addon not in self.addons:
                    self.addons[addon] = False  # Default to disabled

    def scan_plugins(self):
        """Scan the plugin folder and update the plugin list."""
        if os.path.exists(self.plugin_folder):
            plugin_files = [f for f in os.listdir(self.plugin_folder) if f.endswith('.dll')]
            for plugin in plugin_files:
                if plugin not in self.plugins:
                    self.plugins[plugin] = False  # Default to disabled

    def enable_addon(self, addon_name):
        """Enable a specific addon."""
        if addon_name in self.addons:
            self.addons[addon_name] = True
            self.save_config()

    def disable_addon(self, addon_name):
        """Disable a specific addon."""
        if addon_name in self.addons:
            self.addons[addon_name] = False
            self.save_config()

    def enable_plugin(self, plugin_name):
        """Enable a specific plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name] = True
            self.save_config()

    def disable_plugin(self, plugin_name):
        """Disable a specific plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name] = False
            self.save_config()

    def save_changes(self, addons_layout, plugins_layout):
        """Save the current state of addons and plugins."""
        # Save the state of addons
        for i in range(addons_layout.count()):
            widget = addons_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                addon = widget.text()
                self.addons[addon] = widget.isChecked()

        # Save the state of plugins
        for i in range(plugins_layout.count()):
            widget = plugins_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                plugin = widget.text()
                self.plugins[plugin] = widget.isChecked()

        # Save the updated state to the config file
        self.save_config()

        # Confirmation message or debug message
        print("Changes saved to config file.")

    def get_addons(self):
        """Fetch a list of addons from the addon folder, with their enabled/disabled status."""
        if os.path.exists(self.addon_folder):
            addon_dirs = [d for d in os.listdir(self.addon_folder) if os.path.isdir(os.path.join(self.addon_folder, d))]
            for addon in addon_dirs:
                if addon not in self.addons:
                    self.addons[addon] = False  # Default to disabled
        return self.addons

    def get_plugins(self):
        """Fetch a list of plugins from the plugin folder, with their enabled/disabled status."""
        if os.path.exists(self.plugin_folder):
            plugin_files = [f for f in os.listdir(self.plugin_folder) if f.endswith('.dll')]
            for plugin in plugin_files:
                if plugin not in self.plugins:
                    self.plugins[plugin] = False  # Default to disabled
        return self.plugins