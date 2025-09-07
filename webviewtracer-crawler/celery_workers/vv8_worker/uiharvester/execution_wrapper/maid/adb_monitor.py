import logging,subprocess,time
from utils.command_exec import run_command

class ADBMonitor:
    def __init__(self, log_file):
        self.logger = logging.getLogger('ADBMonitor')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        
        self._device_specs = {
            'model': None,
            'serial_number': None,
            'version': None
        }
        
    # Function to check adb device connection
    def is_device_connected(self):
        """Check if ADB is connected and detect device."""
        output = run_command(["adb", "devices"])
        devices = [line.split()[0] for line in output.splitlines() if "\tdevice" in line]
        if devices:
            self.logger.info(f"ADB connected. Device ID: {devices[0]}")
            return True
        else:
            self.logger.error("No devices connected via ADB.")
            print("No devices connected via ADB.")
            return False
    
    # def is_device_connected(self):
    #     try:
    #         output = subprocess.check_output(["adb", "devices"]).decode()
    #         return len(output.splitlines()) > 1 
    #     except subprocess.CalledProcessError:
    #         return False

    def device_info(self):
        adb_is_active = False
        available_devices = []
        message = ""
        try:
            result = run_command(["adb", "devices"])
            devices = [line.split()[0] for line in result.splitlines() if "\tdevice" in line]

            if devices:
                for device_id in devices:
                    model = run_command(["adb", "-s", device_id, "shell", "getprop", "ro.product.model"])
                    serial_number = run_command(["adb", "-s", device_id, "shell", "getprop", "ro.serialno"])
                    versi_andro = run_command(["adb", "-s", device_id, "shell", "getprop", "ro.build.version.release"])
                    available_devices.append({"model": model, "serial_number": serial_number, "versi_andro": versi_andro})
                    self.set_device_specs(model, serial_number, versi_andro)
                adb_is_active = True
                message = "Device is available"
        except Exception as e:
            message = f"Error checking Android device connectivity: {e}"
            return False
        # print(available_devices,message)
        return adb_is_active
    

    # Function to check if the Android app is running
    def is_app_running(self,package_name):
        try:
            output = subprocess.check_output(["adb", "shell", "pidof", package_name]).decode().strip()
            return output != ""
        except subprocess.CalledProcessError:
            return False
        
    def reconnect_device(self):
        logging.info("Attempting to reconnect Android device.")
        try:
            subprocess.run(["adb", "kill-server"], check=True)
            time.sleep(2)
            subprocess.run(["adb", "start-server"], check=True)
            time.sleep(5)
            run_command(['adb' ,'wait-for-device'])
            if self.is_device_connected():
                logging.info("Android device reconnected successfully.")
            else:
                logging.error("Failed to reconnect Android device.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error reconnecting Android device: {e}")

    def get_device_specs(self):
        """Get the current device specifications."""
        return self._device_specs
    
    def set_device_specs(self, model, serial_number, version):
        """Set the device specifications."""
        self._device_specs['model'] = model.strip()
        self._device_specs['serial_number'] = serial_number.strip()
        self._device_specs['version'] = version.strip()