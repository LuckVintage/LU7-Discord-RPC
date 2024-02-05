import base64
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
)
from PyQt5.QtCore import Qt, QTimer, QUrl, QByteArray
from PyQt5.QtGui import QPalette, QColor, QIcon, QDesktopServices, QPixmap, QImage, QIcon, QKeySequence
import rpc
import time
from time import mktime
import os
import requests
import json
import pygetwindow as gw
import psutil
from pynput import keyboard

class DiscordRPCApp(QWidget):
    def __init__(self):
        super().__init__()

        self.tray_update_triggered = False  # Initialize tray_update_triggered
        self.rpc_started = False  # Initialize rpc_started attribute
        self.init_hotkey() # Initialize the hotkey

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
        self.toggle_button.setToolTip("Starts the RPC when clicked. You can also use CTRL+T.")
        self.toggle_button.setStyleSheet("""
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
""")

        self.current_status_label = QLabel("Current Status: Stopped")
        self.current_status_label.setStyleSheet("color: red;")

        self.version_label = QLabel("v1.0.7-alpha - 05 Feb 24")
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
        layout.addRow(self.client_id_label, self.client_id_entry)
        layout.addRow(self.state_label, self.state_entry)
        layout.addRow(self.small_text_label, self.small_text_entry)
        layout.addRow(self.small_image_label, self.small_image_entry)
        layout.addRow(self.large_text_label, self.large_text_entry)
        layout.addRow(self.large_image_label, self.large_image_entry)
        layout.addRow(self.include_timestamp_checkbox)  # Add the checkbox to the layout
        # Add preset buttons with styles
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
        self.save_preset_button.setToolTip("Save the current data as a preset. You can also use CTRL+S.")
        self.save_preset_button.setStyleSheet("""
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
        """)

        self.load_preset_button = QPushButton("Load Preset")
        self.load_preset_button.clicked.connect(self.load_preset)
        self.load_preset_button.setToolTip("Load a previously saved preset. You can also use CTRL+L.")
        self.load_preset_button.setStyleSheet("""
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
        """)

        # Create "Update Presence" button
        self.update_presence_button = QPushButton("Update Presence")
        self.update_presence_button.setObjectName("updatePresenceButton")
        self.update_presence_button.clicked.connect(self.update_presence)
        self.update_presence_button.setStyleSheet("""
            QPushButton#updatePresenceButton {
                background-color: purple;
                color: #FFFFFF;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton#updatePresenceButton:hover {
                background-color: #4C00A4;
            }
        """)

        # Initially hide the "Update Presence" button
        self.update_presence_button.hide()

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_preset_button)
        button_layout.addWidget(self.load_preset_button)

        # Add the horizontal layout to the main form layout
        layout.addRow(button_layout)

        layout.addRow(self.toggle_button)
        layout.addRow(self.update_presence_button)
        layout.addRow(self.current_status_label)
        layout.setVerticalSpacing(5)
        layout.addRow(self.version_label)
        layout.addRow(self.prodwarning_label)


        self.setLayout(layout)

        # Load data from file
        self.load_data()

        # Check for updates using QTimer after a short delay (adjust as needed)
        QTimer.singleShot(3000, self.check_for_updates)

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())

        # Set application icon
        icon_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "logo.icns"
        )
        self.setWindowIcon(QIcon(icon_path))

        # Set background and foreground colors
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # White background
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Black text
        self.setPalette(palette)

        # Apply stylesheet
        stylesheet = """
QWidget {
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

        # Convert the icon image to base64
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.icns")
        with open(icon_path, "rb") as image_file:
            icon_base64 = base64.b64encode(image_file.read()).decode()

        # Convert the base64 string to bytes before passing it to fromBase64
        icon_data = QByteArray.fromBase64(icon_base64.encode())

        # Use the base64-encoded image for the tray icon
        self.tray_icon.setIcon(QIcon(QPixmap.fromImage(QImage.fromData(icon_data))))

        # Create a context menu for the system tray icon
        tray_menu = QMenu(self)

        # Store the reference to the tray action
        self.toggle_rpc_action = tray_menu.addAction("Start Current RPC" if not self.rpc_started else "Stop Current RPC")
        self.toggle_rpc_action.triggered.connect(self.toggle_rpc)

        # Add a divider
        tray_menu.addSeparator()

        # Add "Check for Updates" action to the context menu
        check_updates_action = tray_menu.addAction("Check for Updates")
        check_updates_action.triggered.connect(self.check_for_updates_from_tray)

        open_data_folder_action = tray_menu.addAction("Open Data Folder")
        open_data_folder_action.triggered.connect(self.open_data_folder)

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
        self.load_preset_hotkey .activated.connect(self.load_preset)

    def check_for_updates_from_tray(self):
        # Set the class-level variable to True when updates are checked from the tray
        self.tray_update_triggered = True
        self.check_for_updates()

    def toggle_rpc(self):
        if self.rpc_started:
            self.stop_rpc()
        else:
            if self.client_id_entry.text() and self.state_entry.text():
                self.start_rpc()
            else:
                QMessageBox.warning(self, "Input Error", "You can't start the RPC without entering a Client ID and State.")

        # Update the text of the tray button based on the new RPC state
        toggle_rpc_action = self.tray_icon.contextMenu().actions()[0]
        toggle_rpc_action.setText("Stop Current RPC" if self.rpc_started else "Start Current RPC")

        # Show or hide the "Update Presence" button based on RPC state
        self.update_presence_button.setVisible(self.rpc_started)

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
                QMessageBox.warning(self, "Input Error", "You can't start the RPC without entering a Client ID and State.")

        # Update the text of the tray button based on the new RPC state
        self.toggle_rpc_action.setText("Stop Current RPC" if self.rpc_started else "Start Current RPC")

        # Show or hide the "Update Presence" button based on RPC state
        self.update_presence_button.setVisible(self.rpc_started)

    def start_rpc(self):
        self.client_id = self.client_id_entry.text()
        self.state_text = self.state_entry.text()

        if self.client_id and self.state_text:
            try:
                self.rpc_obj = rpc.DiscordIpcClient.for_platform(self.client_id)
                self.start_time = mktime(time.localtime())
                self.update_rpc_activity()
                self.update_status_label()
                self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: #FFFFFF;
                    padding: 10px 15px;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: darkred;
                }
                """)
                self.toggle_button.setText("Stop RPC")
                self.tray_icon.showMessage("RPC Started", "RPC started successfully.", QSystemTrayIcon.Information, 5000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error starting RPC: {str(e)}.",
                )
        else:
            QMessageBox.warning(self, "Input Error", "You must fill in your Client ID and State before starting the RPC.")

    def stop_rpc(self):
        try:
            if self.rpc_obj:
                self.rpc_obj.close()
                self.rpc_obj = None  # Set to None after stopping
                self.update_status_label()
                self.toggle_button.setStyleSheet("""
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
        """)
                self.toggle_button.setText("Start RPC")
                self.tray_icon.showMessage("RPC Stopped", "RPC stopped successfully.", QSystemTrayIcon.Information, 5000)
            
            else:
                QMessageBox.warning(self, "Warning", "No active RPC to stop.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping RPC: {str(e)}")

    def update_presence(self):
        if self.client_id_entry.text() and self.state_entry.text():
            # Stop and start the RPC again to update the presence
            self.update_rpc_activity()
            QMessageBox.information(self, "Update Success", "Presence updated successfully.")
        else:
            QMessageBox.warning(self, "Input Error", "You can't update the RPC without entering a Client ID and State.")

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
            json.dump(data, file, indent=4)  # Use json.dump to write data in JSON format

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
                self.include_timestamp_checkbox.setChecked(data.get("include_timestamp", True))
        except FileNotFoundError:
            pass  # Ignore if the file is not found

    def is_discord_running(self):
        try:
            # Check if Discord is running using psutil
            discord_processes = ['Discord', 'Discord Canary', 'Discord PTB']
            
            for process in psutil.process_iter(['pid', 'name']):
                if any(discord_process in process.info['name'] for discord_process in discord_processes):
                    return True

            return False
        except Exception as e:
            print(f"Error checking Discord process: {str(e)}")
            return False

    def check_discord_running(self):
        # Check if Discord is open
        if not self.is_discord_running():
            # Create a blocking QMessageBox
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("LU7 Discord RPC will not function if Discord is not running. You will not be able to set a custom presence unless Discord is open.")
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
            self, 'Save Preset', 'Enter Preset Name:')
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
                json.dump(data, file, indent=4)  # Use json.dump to write data in JSON format

            QMessageBox.information(self, "Success", f"Preset '{preset_name}' saved successfully.")

    def load_preset(self):
        # Load data from a preset slot in 'LU7 RP' folder using JSON format
        preset_list = self.get_available_presets()

        if not preset_list:
            QMessageBox.warning(self, "Warning", "No presets found.")
            return

        preset_name, ok = QInputDialog.getItem(self, "Load Preset", "Select a Preset:", preset_list, 0, False)

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
                self.include_timestamp_checkbox.setChecked(data.get("include_timestamp", True))

                QMessageBox.information(self, "Success", f"Preset '{preset_name}' loaded successfully.")
            except FileNotFoundError:
                QMessageBox.warning(self, "Warning", f"Preset '{preset_name}' not found.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading preset '{preset_name}': {str(e)}")

    def get_available_presets(self):
        # Get a list of available presets
        folder_path = os.path.join(os.path.expanduser("~"), "LU7 RP")
        preset_files = [file for file in os.listdir(folder_path) if file.endswith("_preset.json")]
        return [file.split("_preset.json")[0] for file in preset_files]

    def check_for_updates(self):
        try:
            # Replace 'https://lu7rpcupdate.pages.dev/version.txt' with the URL of the text file containing the latest version number
            update_url = 'https://lu7rpcupdate.pages.dev/version.txt'

            # Fetch the latest version number using requests
            response = requests.get(update_url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            latest_version = response.text.strip()

            # Compare the versions
            if latest_version != self.version_label.text():
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
                msg_box.layout().addWidget(spacer, msg_box.layout().rowCount(), 0, 1, msg_box.layout().columnCount())

                # Add a "Download" button
                download_button = QPushButton("Download now from Github")
                msg_box.addButton(download_button, QMessageBox.AcceptRole)

                # Connect button clicks to corresponding functions
                download_button.clicked.connect(lambda: self.open_download_link('https://github.com/LuckVintage/LU7-Discord-RPC/releases'))
                later_button.clicked.connect(msg_box.reject)

                msg_box.exec_()
            else:
                # Show a message only if updates are manually checked from the tray
                if self.tray_update_triggered:
                    QMessageBox.information(self, "Update Status", f"No updates available. You are using version {self.version_label.text()}.")

        except requests.exceptions.RequestException as e:
            # Print the exception details
            print(f"Error during update check: {str(e)}")

            # Non-blocking message box
            QMessageBox.warning(None, "Update Check Failed", f"Failed to check for updates. Error: {str(e)}")
        finally:
            # Reset the tray_update_triggered variable
            self.tray_update_triggered = False

    def open_download_link(self, link):
        # Open the download link in the default web browser
        QDesktopServices.openUrl(QUrl(link))

if __name__ == "__main__":
    app = QApplication([])
    window = DiscordRPCApp()
    window.setWindowTitle("LU7 Discord RPC")
    window.show()
    window.check_discord_running()
    app.exec_()