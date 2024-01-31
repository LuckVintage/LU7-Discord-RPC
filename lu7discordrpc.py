from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
import rpc
import time
from time import mktime
import os

class DiscordRPCApp(QWidget):
    def __init__(self):
        super().__init__()

        self.client_id_label = QLabel("Client ID:")
        self.client_id_entry = QLineEdit()

        self.state_label = QLabel("State:")
        self.state_entry = QLineEdit()

        self.small_text_label = QLabel("Small Text:")
        self.small_text_entry = QLineEdit()

        self.small_image_label = QLabel("Small Image:")
        self.small_image_entry = QLineEdit()

        self.large_text_label = QLabel("Large Text:")
        self.large_text_entry = QLineEdit()

        self.large_image_label = QLabel("Large Image:")
        self.large_image_entry = QLineEdit()

        self.toggle_button = QPushButton("Start RPC")
        self.toggle_button.clicked.connect(self.toggle_rpc)
        self.toggle_button.setStyleSheet("background-color: green; color: white;")

        self.current_status_label = QLabel("Current Status: Stopped")
        self.current_status_label.setStyleSheet("color: red;")

        self.version_label = QLabel("v1.0.2 - 31 Jan 24")
        self.version_label.setAlignment(Qt.AlignCenter)

        layout = QFormLayout()
        layout.addRow(self.client_id_label, self.client_id_entry)
        layout.addRow(self.state_label, self.state_entry)
        layout.addRow(self.small_text_label, self.small_text_entry)
        layout.addRow(self.small_image_label, self.small_image_entry)
        layout.addRow(self.large_text_label, self.large_text_entry)
        layout.addRow(self.large_image_label, self.large_image_entry)
        layout.addRow(self.toggle_button)
        layout.addRow(self.current_status_label)
        layout.addRow(self.version_label)

        self.setLayout(layout)

        # Load data from file
        self.load_data()

        # Set fixed size policy to prevent resizing
        self.setFixedSize(self.sizeHint())

        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.icns")
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

QPushButton {
    padding: 0px 20px;
    border: none;
    border-radius: 4px;
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

    def start_rpc(self):
        self.client_id = self.client_id_entry.text()
        try:
            self.rpc_obj = rpc.DiscordIpcClient.for_platform(self.client_id)
            self.start_time = mktime(time.localtime())
            self.update_rpc_activity()
            self.update_status_label()
            self.toggle_button.setStyleSheet("background-color: red; color: white;")
            self.toggle_button.setText("Stop RPC")
            QMessageBox.information(self, "Success", "RPC started successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting RPC: {str(e)}. Make sure Discord is currently running!")

    def stop_rpc(self):
        try:
            if self.rpc_obj:
                self.rpc_obj.close()
                self.rpc_obj = None  # Set to None after stopping
                self.update_status_label()
                self.toggle_button.setStyleSheet("background-color: green; color: white;")
                self.toggle_button.setText("Start RPC")
                QMessageBox.information(self, "Success", "RPC stopped successfully. It may take a few seconds for Discord to register the change.")
            else:
                QMessageBox.warning(self, "Warning", "No active RPC to stop.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping RPC: {str(e)}")

    def update_rpc_activity(self):
        activity = {
            "state": self.state_entry.text(),
            "timestamps": {"start": self.start_time},
            "assets": {
                "small_text": self.small_text_entry.text(),
                "small_image": self.small_image_entry.text(),
                "large_text": self.large_text_entry.text(),
                "large_image": self.large_image_entry.text(),
            },
        }
        self.rpc_obj.set_activity(activity)
        self.start_time = mktime(time.localtime())

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
        # Save data to a file
        data = {
            "client_id": self.client_id_entry.text(),
            "state": self.state_entry.text(),
            "small_text": self.small_text_entry.text(),
            "small_image": self.small_image_entry.text(),
            "large_text": self.large_text_entry.text(),
            "large_image": self.large_image_entry.text(),
        }

        file_path = os.path.join(os.path.expanduser("~"), "discord_rpc_data.txt")
        with open(file_path, "w") as file:
            for key, value in data.items():
                file.write(f"{key}={value}\n")

    def load_data(self):
        # Load data from a file
        file_path = os.path.join(os.path.expanduser("~"), "discord_rpc_data.txt")
        try:
            with open(file_path, "r") as file:
                for line in file:
                    key, value = line.strip().split("=")
                    if key == "client_id":
                        self.client_id_entry.setText(value)
                    elif key == "state":
                        self.state_entry.setText(value)
                    elif key == "small_text":
                        self.small_text_entry.setText(value)
                    elif key == "small_image":
                        self.small_image_entry.setText(value)
                    elif key == "large_text":
                        self.large_text_entry.setText(value)
                    elif key == "large_image":
                        self.large_image_entry.setText(value)
        except FileNotFoundError:
            pass  # Ignore if the file is not found

    def closeEvent(self, event):
        # Save data when the application is closed
        self.save_data()
        event.accept()

if __name__ == '__main__':
    app = QApplication([])
    window = DiscordRPCApp()
    window.setWindowTitle("LU7 Discord RPC")
    window.show()
    app.exec_()
