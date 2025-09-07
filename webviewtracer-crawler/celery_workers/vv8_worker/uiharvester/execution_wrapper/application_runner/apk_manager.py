import subprocess
import os

class APKManager:
    def __init__(self, apk_path, log_file):
        self.apk_path = apk_path
        self.log_file = log_file

    def install_apk(self):
        """Install APK from the specified path."""
        try:
            install_cmd = ["adb", "install", "-r", self.apk_path]
            subprocess.run(install_cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"APK installation failed: {e}")
            return False

    def extract_package_name(self):
        """Extract package name from APK."""
        try:
            result = subprocess.run(["aapt", "dump", "badging", self.apk_path], stdout=subprocess.PIPE, text=True)
            for line in result.stdout.splitlines():
                if line.startswith("package:"):
                    return line.split("name='")[1].split("'")[0]
        except Exception as e:
            print(f"Failed to extract package name: {e}")
            return None

    def start_application(self, package_name):
        """Start the application by its package name."""
        try:
            start_cmd = ["adb", "shell", "am", "start", "-n", f"{package_name}/.MainActivity"]
            subprocess.run(start_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to start application: {e}")
