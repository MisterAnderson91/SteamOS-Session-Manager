import sys
import json
import urllib.request
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QMessageBox)

class UpdateCheckerThread(QThread):
    update_checked = pyqtSignal(str, str)

    def __init__(self, repo_owner, repo_name, current_version):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version

    def run(self):
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        try:
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "SteamOS-Session-Manager-Updater"}
            )
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "").strip()
                html_url = data.get("html_url", "").strip()
                if latest_tag and latest_tag != self.current_version:
                    self.update_checked.emit(latest_tag, html_url)
        except Exception:
            pass

class SessionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.current_app_version = "2026.07.27"
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('SteamOS Session Manager')
        self.setFixedSize(350, 220)
        
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
        layout.addSpacing(10)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)
        
        # Bottom Layout (Update notification on left, About button on right)
        about_layout = QHBoxLayout()
        
        # Update Notification Label (Hidden by default)
        self.update_label = QLabel()
        self.update_label.setStyleSheet("color: #4da6ff; font-weight: bold;")
        self.update_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_label.hide()
        about_layout.addWidget(self.update_label)
        
        about_layout.addStretch() # Pushes About button to the right
        
        self.about_button = QPushButton("About")
        self.about_button.setFlat(True) 
        self.about_button.setStyleSheet("color: #888888;") 
        self.about_button.clicked.connect(self.show_about)
        about_layout.addWidget(self.about_button)
        
        layout.addLayout(about_layout)
        self.setLayout(layout)

        # Trigger background update check safely after UI loads
        self.start_update_check("MisterAnderson91", "SteamOS-Session-Manager")

    def start_update_check(self, owner, repo):
        self.update_thread = UpdateCheckerThread(owner, repo, self.current_app_version)
        self.update_thread.update_checked.connect(self.display_update_notification)
        self.update_thread.start()

    def display_update_notification(self, latest_version, url):
        self.release_url = url
        self.update_label.setText(f"🚀 Update v{latest_version} available!")
        self.update_label.mousePressEvent = lambda event: self.open_url(self.release_url)
        self.update_label.show()

    def open_url(self, url):
        env = os.environ.copy() if 'os' in sys.modules else {}
        for k in ["LD_LIBRARY_PATH", "APPDIR", "APPIMAGE"]:
            env.pop(k, None)
        try:
            subprocess.Popen(["xdg-open", url], env=env)
        except Exception:
            pass
        
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
        if mode_arg == "desktop":
            try:
                result = subprocess.run(["steamosctl", "get-default-desktop-session"], 
                                        capture_output=True, text=True, check=True)
                current_session = result.stdout.strip()
                
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
                pass 
            except Exception:
                pass 

        try:
            subprocess.run(["steamosctl", "set-default-login-mode", mode_arg], check=True)
            self.status_label.setText(f"Current Boot Mode: {self.get_current_mode()}")
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
