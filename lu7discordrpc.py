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
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon, QDesktopServices
import rpc
import time
from time import mktime
import os
import requests
import json



class DiscordRPCApp(QWidget):
    def __init__(self):
        super().__init__()

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

        self.toggle_button = QPushButton("Start RPC")
        self.toggle_button.setObjectName(
            "toggleButton"
        )  # Set an object name for the toggle button
        self.toggle_button.clicked.connect(self.toggle_rpc)
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

        self.version_label = QLabel("v1.0.5-alpha - 03 Feb 24")
        self.prodwarning_label = QLabel("WARNING: NOT PRODUCTION READY!")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.prodwarning_label.setAlignment(Qt.AlignCenter)

        # Set minimum height for QLabel widgets
        self.client_id_label.setMinimumHeight(40)
        self.state_label.setMinimumHeight(40)
        self.small_text_label.setMinimumHeight(40)
        self.small_image_label.setMinimumHeight(40)
        self.large_text_label.setMinimumHeight(40)
        self.large_image_label.setMinimumHeight(40)
        self.prodwarning_label.setFixedSize(260, 20)


        # set fixed height for QLineEdit
        self.client_id_entry.setFixedSize(140, 25)
        self.state_entry.setFixedSize(140, 25)
        self.small_text_entry.setFixedSize(140, 25)
        self.small_image_entry.setFixedSize(140, 25)
        self.large_text_entry.setFixedSize(140, 25)
        self.large_image_entry.setFixedSize(140, 25)

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
        # Add preset buttons with styles
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_preset)
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
        QTimer.singleShot(5000, self.check_for_updates)

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

        # Initialize RPC object to None
        self.rpc_obj = None
        self.rpc_started = False  # Added variable to track RPC state

    def toggle_rpc(self):
        if self.rpc_started:
            self.stop_rpc()
        else:
            self.start_rpc()

        # Show or hide the "Update Presence" button based on RPC state
        self.update_presence_button.setVisible(self.rpc_started)

    def start_rpc(self):
        self.client_id = self.client_id_entry.text()
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
            QMessageBox.information(self, "Success", "RPC started successfully.")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error starting RPC: {str(e)}. Make sure Discord is currently running!",
            )

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
                QMessageBox.information(
                    self,
                    "Success",
                    "RPC stopped successfully. It may take a few seconds for Discord to register the change.",
                )
            else:
                QMessageBox.warning(self, "Warning", "No active RPC to stop.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping RPC: {str(e)}")

    def update_presence(self):
        # Stop and start the RPC again to update the presence
        self.update_rpc_activity()
        QMessageBox.information(self, "Update Success", "Presence updated successfully.")

    def update_rpc_activity(self):
        current_time = mktime(time.localtime())
        activity = {
            "state": self.state_entry.text(),
            "timestamps": {"start": current_time},
            "assets": {
                "small_text": self.small_text_entry.text(),
                "small_image": self.small_image_entry.text(),
                "large_text": self.large_text_entry.text(),
                "large_image": self.large_image_entry.text(),
            },
        }
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
        except FileNotFoundError:
            pass  # Ignore if the file is not found

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

        except requests.exceptions.RequestException as e:
            # Print the exception details
            print(f"Error during update check: {str(e)}")

            # Non-blocking message box
            QMessageBox.warning(None, "Update Check Failed", f"Failed to check for updates. Error: {str(e)}")

    def open_download_link(self, link):
        # Open the download link in the default web browser
        QDesktopServices.openUrl(QUrl(link))


if __name__ == "__main__":
    app = QApplication([])
    window = DiscordRPCApp()
    window.setWindowTitle("LU7 Discord RPC")
    window.show()
    app.exec_()