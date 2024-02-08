from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFormLayout,
    QMessageBox,
    QSizePolicy,
    QInputDialog,
    QListWidget,
    QHBoxLayout,
    QCheckBox,
    QSystemTrayIcon,
    QMenu,
    QShortcut,
    QDialog,
    QToolButton,
    QAction,
    QTextEdit,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QTimer, QUrl, QByteArray
from PyQt5.QtGui import (
    QPalette,
    QColor,
    QIcon,
    QDesktopServices,
    QPixmap,
    QImage,
    QIcon,
    QKeySequence,
)
import rpc
import time
from time import mktime
import os
import requests
import json
import pygetwindow as gw
import psutil
from pynput import keyboard
import qtawesome
import platform
import shutil
from functools import partial
import sys

version = "v1.1.0-alpha - 08 Feb 24"

if sys.platform == "darwin":
    modifier_key = "⌘"
else:
    modifier_key = "CTRL"


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.init_ui()

        # Load settings data
        self.load_settings()

    def init_ui(self):
        # Create a tickbox called 'Automatically check for updates' with a default of checked
        self.auto_update_checkbox = QCheckBox(
            "Automatically check for updates on start-up"
        )
        self.auto_update_checkbox.setChecked(True)

        # Create a save settings button
        self.save_settings_button = QPushButton(
            qtawesome.icon("fa5s.save", color="white"), "Save Settings"
        )
        self.save_settings_button.clicked.connect(self.save_settings)
        self.save_settings_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.save_settings_button.setToolTip("Saves the above settings.")
        self.save_settings_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        )

        # Create a close window button
        self.close_window_button = QPushButton(
            qtawesome.icon("fa5s.times", color="white"), "Close Window"
        )
        self.close_window_button.clicked.connect(self.close)
        self.close_window_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.close_window_button.setToolTip("Closes the settings window.")
        self.close_window_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """
        )

        # Add the buttons to the layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_settings_button)
        button_layout.addWidget(self.close_window_button)

        # Add layout to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.auto_update_checkbox)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())

    def save_settings(self):
        # Save settings data to 'settings.json' file
        data = {"auto_update": self.auto_update_checkbox.isChecked()}
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "settings.json")
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        # Show a pop-up window
        QMessageBox.information(self, "Settings Saved", "Settings saved successfully.")

    def load_settings(self):
        # Load settings data from 'settings.json' file
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        file_path = os.path.join(folder_path, "settings.json")

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                auto_update = data.get("auto_update", True)
                self.auto_update_checkbox.setChecked(auto_update)
                return data  # Return the loaded settings
        except FileNotFoundError:
            # Create the directory if it doesn't exist
            os.makedirs(folder_path, exist_ok=True)
            # Create the file with default data
            default_data = {"auto_update": True}
            with open(file_path, "w") as file:
                json.dump(default_data, file, indent=4)

            return default_data  # Return the default data


class DiscordRPCApp(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_window = SettingsWindow(parent=self)
        self.setObjectName("mainWindow")  # Initialize main application window
        self.tray_update_triggered = False  # Initialize tray_update_triggered
        self.rpc_started = False  # Initialize rpc_started attribute
        self.init_hotkey()  # Initialize the hotkey

        self.client_id_label = QLabel("Client ID:")
        self.client_id_entry = QLineEdit()
        self.client_id_label.setToolTip(
            "You can find this as the 'Application ID' in the Discord Developer Portal"
        )
        self.client_id_entry.setToolTip(
            "You can find this as the 'Application ID' in the Discord Developer Portal"
        )

        self.state_label = QLabel("State:")
        self.state_entry = QLineEdit()
        self.state_label.setToolTip("Enter any text you like here")
        self.state_entry.setToolTip("Enter any text you like here")

        self.small_text_label = QLabel("Small Text:")
        self.small_text_entry = QLineEdit()
        self.small_text_label.setToolTip(
            "This is the text that shows up when you hover your mouse over the small image"
        )
        self.small_text_entry.setToolTip(
            "This is the text that shows up when you hover your mouse over the small image"
        )

        self.small_image_label = QLabel("Small Image:")
        self.small_image_entry = QLineEdit()
        self.small_image_label.setToolTip(
            "This is the name of the image you would like. It must match exactly one of the images uploaded in the Discord Developer Portal."
        )
        self.small_image_entry.setToolTip(
            "This is the name of the image you would like. It must match exactly one of the images uploaded in the Discord Developer Portal."
        )

        self.large_text_label = QLabel("Large Text:")
        self.large_text_entry = QLineEdit()
        self.large_text_label.setToolTip(
            "This is the text that shows up when you hover your mouse over the large image"
        )
        self.large_text_entry.setToolTip(
            "This is the text that shows up when you hover your mouse over the large image"
        )

        self.large_image_label = QLabel("Large Image:")
        self.large_image_entry = QLineEdit()
        self.large_image_label.setToolTip(
            "This is the name of the image you would like. It must match exactly one of the images uploaded in the Discord Developer Portal."
        )
        self.large_image_entry.setToolTip(
            "This is the name of the image you would like. It must match exactly one of the images uploaded in the Discord Developer Portal."
        )

        self.include_timestamp_checkbox = QCheckBox("Include Timestamp")
        self.include_timestamp_checkbox.setToolTip(
            "This is the 'Time elapsed' text on Discord."
        )
        self.include_timestamp_checkbox.setChecked(True)  # Set default to checked

        self.toggle_button = QPushButton("Start RPC")
        self.toggle_button.setObjectName(
            "toggleButton"
        )  # Set an object name for the toggle button
        self.toggle_button.clicked.connect(self.toggle_rpc)
        self.toggle_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.toggle_button.setToolTip(
            "Starts the RPC when clicked. You can also use {}+T.".format(modifier_key)
        )
        self.toggle_button.setStyleSheet(
            """
    QPushButton#toggleButton {
        background-color: green;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 4px;
    }
    QPushButton#toggleButton:hover {
        background-color: darkgreen;
    }
"""
        )

        # Set the 'play' icon for the initial state
        toggle_icon_name = "play" if not self.rpc_started else "stop"
        self.toggle_button.setIcon(QIcon())  # Clear existing icon
        self.toggle_button.setIcon(
            qtawesome.icon(f"fa5s.{toggle_icon_name}", color="white")
        )
        self.current_status_label = QLabel("Current Status: Stopped")
        self.current_status_label.setStyleSheet("color: red;")

        self.version_label = QLabel(version)
        self.prodwarning_label = QLabel("WARNING: NOT PRODUCTION READY!")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.prodwarning_label.setAlignment(Qt.AlignCenter)

        # Set minimum height for QLabel widgets
        self.client_id_label.setMinimumHeight(40)
        self.state_label.setMinimumHeight(40)
        self.small_text_label.setMinimumHeight(40)
        self.small_image_label.setMinimumHeight(40)
        self.large_text_label.setMinimumHeight(40)
        self.large_image_label.setMinimumHeight(30)
        self.include_timestamp_checkbox.setMinimumHeight(40)

        # set fixed height for QLineEdit
        self.client_id_entry.setFixedSize(140, 25)
        self.state_entry.setFixedSize(140, 25)
        self.small_text_entry.setFixedSize(140, 25)
        self.small_image_entry.setFixedSize(140, 25)
        self.large_text_entry.setFixedSize(140, 25)
        self.large_image_entry.setFixedSize(140, 25)
        self.prodwarning_label.setFixedSize(260, 20)

        # Set alignment to the top
        self.client_id_label.setAlignment(Qt.AlignTop)
        self.state_label.setAlignment(Qt.AlignTop)
        self.small_text_label.setAlignment(Qt.AlignTop)
        self.small_image_label.setAlignment(Qt.AlignTop)
        self.large_text_label.setAlignment(Qt.AlignTop)
        self.large_image_label.setAlignment(Qt.AlignTop)

        self.client_id_entry.setToolTipDuration(
            5000
        )  # Set tooltip duration in milliseconds
        self.state_entry.setToolTipDuration(5000)
        self.small_text_entry.setToolTipDuration(5000)
        self.small_image_entry.setToolTipDuration(5000)
        self.large_text_entry.setToolTipDuration(5000)
        self.large_image_entry.setToolTipDuration(5000)

        layout = QFormLayout()

        # Create the settings button
        cog_icon = qtawesome.icon("fa.cog", color="grey")
        self.settings_icon = QLabel()
        self.settings_icon.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.settings_icon.setPixmap(cog_icon.pixmap(20, 20))
        self.settings_icon.setToolTip("Click to open Settings")
        self.settings_icon.mousePressEvent = lambda event: self.show_settings_window()

        # Create the open data folder button
        open_folder_icon = qtawesome.icon("fa.folder-open", color="grey")
        self.open_folder_icon = QLabel()
        self.open_folder_icon.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.open_folder_icon.setPixmap(open_folder_icon.pixmap(20, 20))
        self.open_folder_icon.setToolTip("Click to open data folder")
        self.open_folder_icon.mousePressEvent = lambda event: self.open_data_folder()

        # Create the import/export window button
        import_export_window_icon = qtawesome.icon("fa5s.file-archive", color="grey")
        self.import_export_window_icon = QLabel()
        self.import_export_window_icon.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.import_export_window_icon.setPixmap(
            import_export_window_icon.pixmap(20, 20)
        )
        self.import_export_window_icon.setToolTip("Import or Export your data")
        self.import_export_window_icon.mousePressEvent = (
            lambda event: self.show_import_export_data__window()
        )

        # Create a horizontal layout for the settings icon and current status
        status_and_settings_layout = QHBoxLayout()
        status_and_settings_layout.addWidget(self.current_status_label)
        status_and_settings_layout.addStretch()  # Add stretch to push the settings icon to the right
        status_and_settings_layout.addWidget(self.settings_icon)
        status_and_settings_layout.addWidget(self.import_export_window_icon)
        status_and_settings_layout.addWidget(self.open_folder_icon)

        # Add the bottom-right layout to the main form layout
        layout = QFormLayout()

        layout.addRow(self.client_id_label, self.client_id_entry)
        layout.addRow(self.state_label, self.state_entry)
        layout.addRow(self.small_text_label, self.small_text_entry)
        layout.addRow(self.small_image_label, self.small_image_entry)
        layout.addRow(self.large_text_label, self.large_text_entry)
        layout.addRow(self.large_image_label, self.large_image_entry)
        layout.addRow(self.include_timestamp_checkbox)  # Add the checkbox to the layout
        # Add preset buttons with styles
        self.save_preset_button = QPushButton(
            qtawesome.icon("fa5s.save", color="white"), "Save Preset"
        )
        self.save_preset_button.clicked.connect(self.save_preset)
        self.save_preset_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.save_preset_button.setToolTip(
            "Save the current data as a preset. You can also use {}+S.".format(
                modifier_key
            )
        )
        self.save_preset_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        )

        self.load_preset_button = QPushButton(
            qtawesome.icon("fa5s.download", color="white"), "Load Preset"
        )
        self.load_preset_button.clicked.connect(self.load_preset)
        self.load_preset_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.load_preset_button.setToolTip(
            "Load a previously saved preset. You can also use {}+L.".format(
                modifier_key
            )
        )
        self.load_preset_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        )

        # Create "Update Presence" button
        self.update_presence_button = QPushButton(
            qtawesome.icon("fa5s.sync-alt", color="white"), "Update Presence"
        )
        self.update_presence_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.update_presence_button.setObjectName("updatePresenceButton")
        self.update_presence_button.clicked.connect(self.update_presence)
        self.update_presence_button.setStyleSheet(
            """
            QPushButton#updatePresenceButton {
                background-color: purple;
                color: #FFFFFF;
                padding: 100% 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton#updatePresenceButton:hover {
                background-color: #4C00A4;
            }
        """
        )

        # Initially hide the "Update Presence" button
        self.update_presence_button.hide()

        # Create a horizontal layout for the preset buttons
        preset_button_layout = QHBoxLayout()
        preset_button_layout.addWidget(self.save_preset_button)
        preset_button_layout.addSpacing(5)  # Add spacing between the buttons
        preset_button_layout.addWidget(self.load_preset_button)

        # Add the horizontal layout to the main form layout
        layout.addRow(preset_button_layout)

        layout.addRow(self.toggle_button)
        layout.addRow(self.update_presence_button)
        layout.addRow(status_and_settings_layout)
        layout.setVerticalSpacing(5)
        layout.addRow(self.version_label)
        layout.addRow(self.prodwarning_label)

        self.setLayout(layout)

        # Load data from file
        self.load_data()

        # Check for updates using QTimer after a short delay (adjust as needed)
        if self.settings_window.load_settings().get("auto_update", False):
            QTimer.singleShot(3000, self.check_for_updates)

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())

        # Set application icon
        icon_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logo.png"
        )
        self.setWindowIcon(QIcon(icon_path))

        # Set background and foreground colors
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # White background
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Black text
        self.setPalette(palette)

        # Apply stylesheet
        stylesheet = """

 #mainWindow {
    background-color: #f0f0f0;
    color: #333;
    font-family: Arial, sans-serif;
}

QLineEdit {
    padding: 0;
    border: 1px solid #ccc;
    border-radius: 4px;
}

QLabel {
    font-size: 14px;
    margin-bottom: 8px;
}
"""

        self.setStyleSheet(stylesheet)

        # Create a system tray icon
        self.create_system_tray_icon()

    def create_system_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)

        # Use the image for the tray icon
        self.tray_icon.setIcon(
            QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.png"))
        )

        # Create a context menu for the system tray icon
        tray_menu = QMenu(self)

        # Store the reference to the tray action
        self.toggle_rpc_action = tray_menu.addAction(
            "Start Current RPC" if not self.rpc_started else "Stop Current RPC"
        )
        self.toggle_rpc_action.triggered.connect(self.toggle_rpc)

        # Add a divider
        tray_menu.addSeparator()

        # Add a non-clickable action for update status to the context menu
        self.update_status_action = QAction("You are running the latest version", self)
        self.update_status_action.setEnabled(False)  # Make it non-clickable initially
        tray_menu.addAction(self.update_status_action)

        # Add "Check for Updates" action to the context menu
        check_updates_action = tray_menu.addAction("Check for Updates")
        check_updates_action.triggered.connect(self.check_for_updates_from_tray)

        # Add "Settings" action to the context menu
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings_window)

        # Add "About" action to the context menu
        settings_action = tray_menu.addAction("About")
        settings_action.triggered.connect(self.show_about_window)

        # Add a divider
        tray_menu.addSeparator()

        # Add "Export" action to the context menu
        settings_action = tray_menu.addAction("Export data")
        settings_action.triggered.connect(self.export_data)

        # Add "Import" action to the context menu
        settings_action = tray_menu.addAction("Import data")
        settings_action.triggered.connect(self.import_data_dialog)

        # Add a divider
        tray_menu.addSeparator()

        open_data_folder_action = tray_menu.addAction("Open Data Folder")
        open_data_folder_action.triggered.connect(self.open_data_folder)

        # Add "GitHub Repository" action to the context menu
        github_action = tray_menu.addAction("Github")
        github_action.triggered.connect(self.open_github_repository)

        # Add a divider
        tray_menu.addSeparator()

        # Add "Exit" action to the context menu
        exit_action = tray_menu.addAction("Quit")
        exit_action.triggered.connect(self.exit_application)

        # Set the context menu for the system tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Show the system tray icon
        self.tray_icon.show()

    def exit_application(self):
        # Close the application when "Exit" is selected from the system tray menu
        self.save_data()  # Save data before exiting
        self.tray_icon.hide()
        self.close()

    def init_hotkey(self):
        # Toggle RPC hotkey
        self.toggle_hotkey = QShortcut(QKeySequence("Ctrl+T"), self)
        self.toggle_hotkey.activated.connect(self.toggle_rpc)

        # Save preset hotkey
        self.save_preset_hotkey = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_preset_hotkey.activated.connect(self.save_preset)

        # Load Preset hotkey
        self.load_preset_hotkey = QShortcut(QKeySequence("Ctrl+L"), self)
        self.load_preset_hotkey.activated.connect(self.load_preset)

    def open_github_repository(self):
        github_url = "https://github.com/LuckVintage/LU7-Discord-RPC"
        QDesktopServices.openUrl(QUrl(github_url))

    def check_for_updates_from_tray(self):
        # Set the class-level variable to True when updates are checked from the tray
        self.tray_update_triggered = True
        self.check_for_updates()

    def show_settings_window(self):
        # Instantiate and show the SettingsWindow
        self.settings_window = SettingsWindow(self)
        self.settings_window.exec_()

    def show_import_export_data__window(self):
        # Instantiate and show the SettingsWindow
        self.settings_window = ImportExportDataWindow(self)
        self.settings_window.exec_()

    def show_about_window(self):
        # Instantiate and show the SettingsWindow
        self.settings_window = AboutWindow(self)
        self.settings_window.exec_()

    def import_data_dialog(self):
        # Open a file dialog for the user to select the zip file to import
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Zip files (*.zip)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                zip_path = selected_files[0]
                self.import_data(zip_path)

    def export_data(self):
        # Open a file dialog for the user to select the destination folder
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        folder_dialog.setWindowTitle("Select Export Folder")
        if folder_dialog.exec_():
            selected_folder = folder_dialog.selectedFiles()
            if selected_folder:
                export_folder = selected_folder[0]

                # Get the path of the LU7 RP folder
                folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")

                # Create a zip file containing all files and subdirectories in the LU7 RP folder
                shutil.make_archive("LU7_RP_data", "zip", folder_path)

                # Move the zip file to the selected export folder
                shutil.move(
                    "LU7_RP_data.zip", os.path.join(export_folder, "LU7_RP_data.zip")
                )

                QMessageBox.information(
                    self,
                    "Export Successful",
                    "Data exported successfully.",
                )

    def import_data(self, zip_path):
        # Get the path of the LU7 RP folder
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")

        # Extract the contents of the zip file to the LU7 RP folder
        shutil.unpack_archive(zip_path, folder_path, "zip")

        QMessageBox.information(
            self,
            "Import Successful",
            "Data imported successfully.",
        )

    def toggle_rpc(self):
        if self.rpc_started:
            self.stop_rpc()
        else:
            if self.client_id_entry.text() and self.state_entry.text():
                self.start_rpc()
            else:
                QMessageBox.warning(
                    self,
                    "Input Error",
                    "You can't start the RPC without entering a Client ID and State.",
                )

        # Update the text of the tray button based on the new RPC state
        self.toggle_rpc_action.setText(
            "Stop Current RPC" if self.rpc_started else "Start Current RPC"
        )

        # Show or hide the "Update Presence" button based on RPC state
        self.update_presence_button.setVisible(self.rpc_started)

        # Update the toggle button's icon based on RPC state
        toggle_icon_name = "stop" if self.rpc_started else "play"  # Fixed this line
        self.toggle_button.setIcon(QIcon())  # Clear existing icon
        toggle_icon = qtawesome.icon(f"fa5s.{toggle_icon_name}", color="white")
        self.toggle_button.setIcon(toggle_icon)

        # Initialize RPC object to None
        self.rpc_obj = None
        self.rpc_started = False  # Added variable to track RPC state

    def open_data_folder(self):
        # Open the folder where data is stored using the default file explorer
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def toggle_rpc(self):
        if self.rpc_started:
            self.stop_rpc()
        else:
            if self.client_id_entry.text() and self.state_entry.text():
                self.start_rpc()
            else:
                QMessageBox.warning(
                    self,
                    "Input Error",
                    "You can't start the RPC without entering a Client ID and State.",
                )

        # Update the text of the tray button based on the new RPC state
        self.toggle_rpc_action.setText(
            "Stop Current RPC" if self.rpc_started else "Start Current RPC"
        )

        # Show or hide the "Update Presence" button based on RPC state
        self.update_presence_button.setVisible(self.rpc_started)

        # Update the toggle button's icon based on RPC state
        toggle_icon_name = "stop" if self.rpc_started else "play"  # Fixed this line
        self.toggle_button.setIcon(QIcon())  # Clear existing icon
        toggle_icon = qtawesome.icon(f"fa5s.{toggle_icon_name}", color="white")
        self.toggle_button.setIcon(toggle_icon)

    def start_rpc(self):
        self.client_id = self.client_id_entry.text()
        self.state_text = self.state_entry.text()

        if self.client_id and self.state_text:
            try:
                self.rpc_obj = rpc.DiscordIpcClient.for_platform(self.client_id)
                self.start_time = mktime(time.localtime())
                self.update_rpc_activity()
                self.update_status_label()
                self.toggle_button.setStyleSheet(
                    """
                QPushButton {
                    background-color: red;
                    color: #FFFFFF;
                    padding: 100% 15px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: darkred;
                }
                """
                )
                self.toggle_button.setText("Stop RPC")
                self.tray_icon.showMessage(
                    "RPC Started",
                    "RPC started successfully.",
                    QSystemTrayIcon.Information,
                    5000,
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error starting RPC: {str(e)}.",
                )
        else:
            QMessageBox.warning(
                self,
                "Input Error",
                "You must fill in your Client ID and State before starting the RPC.",
            )

    def stop_rpc(self):
        try:
            if self.rpc_obj:
                self.rpc_obj.close()
                self.rpc_obj = None  # Set to None after stopping
                self.update_status_label()
                self.toggle_button.setStyleSheet(
                    """
            QPushButton {
                background-color: green;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
        """
                )
                self.toggle_button.setText("Start RPC")
                self.tray_icon.showMessage(
                    "RPC Stopped",
                    "RPC stopped successfully.",
                    QSystemTrayIcon.Information,
                    5000,
                )

            else:
                QMessageBox.warning(self, "Warning", "No active RPC to stop.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping RPC: {str(e)}")

    def update_presence(self):
        if self.client_id_entry.text() and self.state_entry.text():
            # Stop and start the RPC again to update the presence
            self.update_rpc_activity()
            self.tray_icon.showMessage(
                "Update Success",
                "Presence updated successfully.",
                QSystemTrayIcon.Information,
                5000,
            )
        else:
            QMessageBox.warning(
                self,
                "Input Error",
                "You can't update the RPC without entering a Client ID and State.",
            )

    def update_rpc_activity(self):
        current_time = mktime(time.localtime())
        activity = {"state": self.state_entry.text()}

        if self.include_timestamp_checkbox.isChecked():
            activity["timestamps"] = {"start": current_time}

        # Add assets only if they are not empty
        assets = {
            "small_text": self.small_text_entry.text(),
            "small_image": self.small_image_entry.text(),
            "large_text": self.large_text_entry.text(),
            "large_image": self.large_image_entry.text(),
        }

        non_empty_assets = {key: value for key, value in assets.items() if value}

        if non_empty_assets:
            activity["assets"] = non_empty_assets

        self.rpc_obj.set_activity(activity)
        self.start_time = current_time

    def update_status_label(self):
        if self.rpc_obj:
            self.current_status_label.setText("Current Status: Started")
            self.current_status_label.setStyleSheet("color: green;")
            self.rpc_started = True
        else:
            self.current_status_label.setText("Current Status: Stopped")
            self.current_status_label.setStyleSheet("color: red;")
            self.rpc_started = False

    def save_data(self):
        # Save data to a file in 'LU7 RP' folder using JSON format
        data = {
            "client_id": self.client_id_entry.text(),
            "state": self.state_entry.text(),
            "small_text": self.small_text_entry.text(),
            "small_image": self.small_image_entry.text(),
            "large_text": self.large_text_entry.text(),
            "large_image": self.large_image_entry.text(),
            "include_timestamp": self.include_timestamp_checkbox.isChecked(),
        }

        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, "discord_rpc_data.json")
        with open(file_path, "w") as file:
            json.dump(
                data, file, indent=4
            )  # Use json.dump to write data in JSON format

    def load_data(self):
        # Load data from a file in 'LU7 RP' folder using JSON format
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        file_path = os.path.join(folder_path, "discord_rpc_data.json")

        try:
            with open(file_path, "r") as file:
                data = json.load(file)  # Use json.load to read data in JSON format

                # Update QLineEdit widgets with loaded data
                self.client_id_entry.setText(data.get("client_id", ""))
                self.state_entry.setText(data.get("state", ""))
                self.small_text_entry.setText(data.get("small_text", ""))
                self.small_image_entry.setText(data.get("small_image", ""))
                self.large_text_entry.setText(data.get("large_text", ""))
                self.large_image_entry.setText(data.get("large_image", ""))

                # Update timestamp checkbox
                self.include_timestamp_checkbox.setChecked(
                    data.get("include_timestamp", True)
                )
        except FileNotFoundError:
            pass  # Ignore if the file is not found

    def is_discord_running(self):
        try:
            # Check if Discord is running using psutil
            discord_processes = ["Discord", "Discord Canary", "Discord PTB"]

            for process in psutil.process_iter(["pid", "name"]):
                process_name = process.info["name"].lower()
                if any(
                    discord_process.lower() in process_name
                    for discord_process in discord_processes
                ):
                    return True
        except Exception as e:
            print("Error checking Discord process:", e)  # Debug print
        return False

    def check_discord_running(self):
        # Check if Discord is open
        if not self.is_discord_running():
            # Create a blocking QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(
                "LU7 Discord RPC will not function if Discord is not running. You will not be able to set a custom presence unless Discord is open."
            )
            msg_box.addButton(QMessageBox.Ok)

            # Make the QMessageBox blocking
            msg_box.exec_()

    def closeEvent(self, event):
        # Save data when the application is closed
        self.save_data()
        event.accept()

    def save_preset(self):
        # Save the current data to a preset slot in 'LU7 RP' folder using JSON format
        preset_name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter Preset Name:"
        )
        if ok and preset_name:
            data = {
                "client_id": self.client_id_entry.text(),
                "state": self.state_entry.text(),
                "small_text": self.small_text_entry.text(),
                "small_image": self.small_image_entry.text(),
                "large_text": self.large_text_entry.text(),
                "large_image": self.large_image_entry.text(),
                "include_timestamp": self.include_timestamp_checkbox.isChecked(),
            }

            folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, f"{preset_name}_preset.json")
            with open(file_path, "w") as file:
                json.dump(
                    data, file, indent=4
                )  # Use json.dump to write data in JSON format

            QMessageBox.information(
                self, "Success", f"Preset '{preset_name}' saved successfully."
            )

    def load_preset(self):
        # Load data from a preset slot in 'LU7 RP' folder using JSON format
        preset_list = self.get_available_presets()

        if not preset_list:
            QMessageBox.warning(self, "Warning", "No presets found.")
            return

        preset_name, ok = QInputDialog.getItem(
            self, "Load Preset", "Select a Preset:", preset_list, 0, False
        )

        if ok:
            folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
            file_path = os.path.join(folder_path, f"{preset_name}_preset.json")

            try:
                with open(file_path, "r") as file:
                    data = json.load(file)  # Use json.load to read data in JSON format

                    # Update QLineEdit widgets with loaded data
                    self.client_id_entry.setText(data.get("client_id", ""))
                    self.state_entry.setText(data.get("state", ""))
                    self.small_text_entry.setText(data.get("small_text", ""))
                    self.small_image_entry.setText(data.get("small_image", ""))
                    self.large_text_entry.setText(data.get("large_text", ""))
                    self.large_image_entry.setText(data.get("large_image", ""))

                # Update timestamp checkbox
                self.include_timestamp_checkbox.setChecked(
                    data.get("include_timestamp", True)
                )

                QMessageBox.information(
                    self, "Success", f"Preset '{preset_name}' loaded successfully."
                )
            except FileNotFoundError:
                QMessageBox.warning(
                    self, "Warning", f"Preset '{preset_name}' not found."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error loading preset '{preset_name}': {str(e)}"
                )

    def get_available_presets(self):
        # Get a list of available presets
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        preset_files = [
            file for file in os.listdir(folder_path) if file.endswith("_preset.json")
        ]
        return [file.split("_preset.json")[0] for file in preset_files]

    def check_for_updates(self):
        try:
            # Replace 'https://lu7rpcupdate.pages.dev/version.txt' with the URL of the text file containing the latest version number
            update_url = "https://lu7rpcupdate.pages.dev/version.txt"

            # Fetch the latest version number using requests
            response = requests.get(update_url, headers={"User-Agent": "LU7-RPC-APP"})
            response.raise_for_status()

            latest_version = response.text.strip()

            # Compare the versions
            if latest_version != version:
                self.update_status_action.setText("Update Available")
                # Custom QMessageBox with "Download" and "I'll update later" buttons
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Update Available")
                msg_box.setText(f"A new version ({latest_version}) is available!")
                msg_box.setIcon(QMessageBox.Information)

                # Add a "I'll update later" button
                later_button = QPushButton("I'll update later")
                msg_box.addButton(later_button, QMessageBox.RejectRole)

                # Add a spacer to push the "Download" button to the right
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                msg_box.layout().addWidget(
                    spacer,
                    msg_box.layout().rowCount(),
                    0,
                    1,
                    msg_box.layout().columnCount(),
                )

                # Add a "Download" button
                download_button = QPushButton("Download now from Github")
                msg_box.addButton(download_button, QMessageBox.AcceptRole)

                # Connect button clicks to corresponding functions
                download_button.clicked.connect(
                    lambda: self.open_download_link(
                        "https://github.com/LuckVintage/LU7-Discord-RPC/releases"
                    )
                )
                later_button.clicked.connect(msg_box.reject)

                msg_box.exec_()
            else:
                self.update_status_action.setText("You are running the latest version")
                # Show a message only if updates are manually checked from the tray
                if self.tray_update_triggered:
                    QMessageBox.information(
                        self,
                        "Update Status",
                        f"No updates available. You are using version {self.version_label.text()}.",
                    )

        except requests.exceptions.RequestException as e:
            # Print the exception details
            print(f"Error during update check: {str(e)}")

            # Non-blocking message box
            QMessageBox.warning(
                None,
                "Update Check Failed",
                f"Failed to check for updates. Error: {str(e)}",
            )
        finally:
            # Reset the tray_update_triggered variable
            self.tray_update_triggered = False

    def open_download_link(self, link):
        # Open the download link in the default web browser
        QDesktopServices.openUrl(QUrl(link))


class AboutWindow(QDialog):
    def __init__(self, version_label, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.init_ui()

    def init_ui(self):
        # Create QLabel for logo
        logo_label = QLabel()
        logo_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logo.png"
        )
        pixmap = QPixmap(logo_path).scaled(50, 50, Qt.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("LU7 Discord RPC")
        title_label.setAlignment(Qt.AlignCenter)
        version_label = QLabel(version)
        version_label.setAlignment(Qt.AlignCenter)

        # Create QTextEdit for license
        license_edit = QTextEdit()
        license_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "LICENSE.txt"
        )
        with open(license_path, "r") as file:
            license_text = file.read()
        license_edit.setPlainText(license_text)
        license_edit.setReadOnly(True)

        # Create QLabel for the message with clickable link
        thanks_label = QLabel(
            "Special thanks to <a href='https://github.com/niveshbirangal'>niveshbirangal</a>"
            " for the Python code available at "
            "<a href='https://github.com/niveshbirangal/discord-rpc'>https://github.com/niveshbirangal/discord-rpc</a>."
            " The LU7 Discord RPC app wouldn't be possible without his code contributions!"
        )
        thanks_label.setOpenExternalLinks(True)
        thanks_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        thanks_label.setWordWrap(True)

        copyright_label = QLabel("Copyright \u00A9 Andrew Peacock 2024")
        copyright_label.setAlignment(Qt.AlignCenter)
        # Create a close window button
        self.close_window_button = QPushButton(
            qtawesome.icon("fa5s.times", color="white"), "Close Window"
        )
        self.close_window_button.clicked.connect(self.close)
        self.close_window_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.close_window_button.setToolTip("Closes the about window.")
        self.close_window_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """
        )

        # Add layout to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(title_label)
        main_layout.addWidget(version_label)
        main_layout.addWidget(license_edit)  # Add license text
        main_layout.addWidget(thanks_label)
        main_layout.addWidget(copyright_label)
        main_layout.addWidget(self.close_window_button)
        self.setLayout(main_layout)

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())


class ImportExportDataWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export and Import data")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Create a form layout to hold the buttons
        layout = QFormLayout()

        # Create a close window button
        self.close_window_button = QPushButton(
            qtawesome.icon("fa5s.times", color="white"), "Close Window"
        )
        self.close_window_button.clicked.connect(self.close)
        self.close_window_button.setCursor(
            Qt.PointingHandCursor
        )  # Change cursor to a pointing hand
        self.close_window_button.setToolTip("Closes the window.")
        self.close_window_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """
        )

        # Create "Export Data" button
        self.export_data_button = QPushButton(
            qtawesome.icon("fa5s.arrow-circle-down", color="white"), "Export Data"
        )
        self.export_data_button.setObjectName("exportDataButton")
        # Connect the clicked signal to the export_data method
        self.export_data_button.clicked.connect(
            partial(DiscordRPCApp.export_data, self)
        )
        self.export_data_button.setCursor(Qt.PointingHandCursor)
        self.export_data_button.setToolTip("Export data to a zip file")
        self.export_data_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            """
        )

        # Create "Import Data" button
        self.import_data_button = QPushButton(
            qtawesome.icon("fa5s.arrow-circle-up", color="white"), "Import Data"
        )
        self.export_data_button.setObjectName("exportDataButton")
        self.import_data_button.setObjectName("importDataButton")
        # Connect the clicked signal to the import_data_dialog method
        # Connect the clicked signal to the import_data_dialog method of DiscordRPCApp
        self.import_data_button.clicked.connect(
            partial(DiscordRPCApp.import_data_dialog, self)
        )
        self.import_data_button.setCursor(Qt.PointingHandCursor)
        self.import_data_button.setToolTip("Import data from a zip file")
        self.import_data_button.setStyleSheet(
            """
            QPushButton {
                background-color: #007BFF;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            """
        )

        # Create a horizontal layout for the export and import buttons
        export_import_layout = QHBoxLayout()
        export_import_layout.addWidget(self.export_data_button)
        export_import_layout.addWidget(self.import_data_button)

        # Add the export and import buttons to the form layout
        layout.addRow(export_import_layout)

        # Add the form layout to the main layout
        main_layout.addLayout(layout)

        # Add the close window button to the main layout
        main_layout.addWidget(self.close_window_button)

        # Set the main layout for the dialog
        self.setLayout(main_layout)

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())

    def import_data(self, zip_path):
        # Get the path of the LU7 RP folder
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")

        # Extract the contents of the zip file to the LU7 RP folder
        shutil.unpack_archive(zip_path, folder_path, "zip")

        QMessageBox.information(
            self,
            "Import Successful",
            "Data imported successfully.",
        )


if __name__ == "__main__":
    app = QApplication([])
    window = DiscordRPCApp()
    window.setWindowTitle("LU7 Discord RPC")
    window.show()
    window.check_discord_running()
    app.exec_()
