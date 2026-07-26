import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

class SessionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SteamOS Session Manager')
        self.setFixedSize(350, 220) # Increased height to fit the About button
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Status Label
        self.status_label = QLabel(f"Current Boot Mode: {self.get_current_mode()}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # Mode Buttons
        self.btn_game = QPushButton("Game Mode")
        self.btn_game.clicked.connect(lambda: self.set_mode("game", "Game Mode"))
        layout.addWidget(self.btn_game)
        
        self.btn_desktop = QPushButton("Desktop Mode")
        self.btn_desktop.clicked.connect(lambda: self.set_mode("desktop", "Desktop Mode"))
        layout.addWidget(self.btn_desktop)
        
        # Exit Button
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        self.btn_exit.setStyleSheet("margin-top: 10px;")
        layout.addWidget(self.btn_exit)
        
        # About Layout (Bottom Right)
        about_layout = QHBoxLayout()
        about_layout.addStretch() # Pushes the button to the right
        
        self.about_button = QPushButton("About")
        self.about_button.setFlat(True) 
        # Apply CSS to make the text lower contrast (grey)
        self.about_button.setStyleSheet("color: #888888;") 
        self.about_button.clicked.connect(self.show_about)
        
        about_layout.addWidget(self.about_button)
        layout.addLayout(about_layout)
        
        self.setLayout(layout)
        
    def show_about(self):
        about_text = (
            "About this app:\n\n"
            "This app manages your default boot state on SteamOS using the built-in 'steamosctl' tool.\n\n"
            "• It uses 'steamosctl get-default-login-mode' and 'set-default-login-mode' to switch between Game Mode and Desktop Mode.\n"
            "• When switching to Desktop Mode, it checks your environment using 'steamosctl get-default-desktop-session'.\n"
            "• If an X11 session is detected, it offers to reset it back to the standard Wayland experience using 'steamosctl set-default-desktop-session plasma.desktop'.\n\n"
            "For updates or more information, visit:\n"
            "https://github.com/MisterAnderson91/SteamOS-Session-Manager"
        )
        QMessageBox.information(self, "About SteamOS Session Manager", about_text)

    def get_current_mode(self):
        try:
            # Query steamosctl for the current default login mode
            result = subprocess.run(["steamosctl", "get-default-login-mode"], 
                                    capture_output=True, text=True, check=True)
            mode = result.stdout.strip()
            
            if mode == "game":
                return "Game Mode"
            elif mode == "desktop":
                return "Desktop Mode"
            else:
                return mode.title()
                
        except FileNotFoundError:
            return "Command Not Found"
        except subprocess.CalledProcessError:
            return "Error Reading Mode"
        except Exception:
            return "Unknown"

    def set_mode(self, mode_arg, mode_name):
        # If setting to Desktop Mode, check for X11 first
        if mode_arg == "desktop":
            try:
                result = subprocess.run(["steamosctl", "get-default-desktop-session"], 
                                        capture_output=True, text=True, check=True)
                current_session = result.stdout.strip()
                
                # Check if it's explicitly plasmax11.desktop or contains x11
                if "x11" in current_session.lower() or "plasmax11.desktop" in current_session.lower():
                    reply = QMessageBox.question(
                        self,
                        "WARNING: X11 Session Detected",
                        f"Your system is currently set to use X11 desktop mode ({current_session}).\n\nWould you like to reset it to the default Wayland desktop mode (plasma.desktop)?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        subprocess.run(["steamosctl", "set-default-desktop-session", "plasma.desktop"], check=True)
                        QMessageBox.information(self, "Session Updated", "Desktop session successfully reset to plasma.desktop.")
            
            except FileNotFoundError:
                pass # If steamosctl is missing, let the main block below handle the error gracefully
            except Exception:
                pass # Fail silently here so it still proceeds to change the login mode

        # Proceed to set the actual login mode
        try:
            subprocess.run(["steamosctl", "set-default-login-mode", mode_arg], check=True)
            
            # Refresh the status label
            self.status_label.setText(f"Current Boot Mode: {self.get_current_mode()}")
            
            # Notify the user
            QMessageBox.information(
                self, 
                "Mode Updated", 
                f"Default boot mode successfully changed to {mode_name}.\n\nThis will take effect on your next reboot."
            )
                                    
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "The 'steamosctl' command was not found. Are you running this on SteamOS?")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Execution Error", f"Command failed with exit code {e.returncode}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = SessionSelector()
    window.show()
    
    sys.exit(app.exec())
