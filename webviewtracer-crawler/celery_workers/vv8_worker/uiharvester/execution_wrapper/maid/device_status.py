import logging
from utils.command_exec import run_command

class DeviceStatus:
    def __init__(self, log_file):
        self.logger = logging.getLogger('DeviceStatus')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def check_device_status(self):
        output = run_command(["adb","shell", "su","-c","getprop","sys.boot_completed"])
        if output == '1':
            self.logger.info("Device status: READY.")
            return True
        else:
            self.logger.error("Device status check failed.")
            return False
        
    def check_zygote_status(self):
        zygote64 = run_command(["adb","shell", "su","-c","ps","|","grep","zygote64"])
        # webview_zygote = run_command(["adb","shell", "su","-c","ps","|","grep","webview_zygote"])
        if zygote64:
            self.logger.info("Zygote status: Ready.")
            return True
        else:
            self.logger.error("Zygote status: Not ready.")
            return False
