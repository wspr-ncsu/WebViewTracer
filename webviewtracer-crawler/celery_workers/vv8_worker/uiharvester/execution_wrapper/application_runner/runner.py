import logging
import subprocess
import multiprocessing
from multiprocessing import Manager,Array
import time,os,signal
from datetime import datetime
from application_runner.mode import  TraversingMode
from maid.adb_monitor import ADBMonitor
from maid.device_status import DeviceStatus
from maid.frida_monitor import FridaMonitor
from utils.log_utils import create_log_directory
from utils.command_exec import try_command,run_command,frun_command

class ApplicationRunner:
    def __init__(self, apk_path,max_retries, retry_failed_apps=False):
        log_dir = create_log_directory()
        global log_file
        log_file = f"{log_dir}/application_runner.log"
        self.max_retries = max_retries
        self.logger = logging.getLogger('ApplicationRunner')
        self.retry_failed_apps = retry_failed_apps
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.apk_path = apk_path
        self.adb_monitor = ADBMonitor(log_file)
        self.device_status = DeviceStatus(log_file)
        self.frida_monitor = FridaMonitor(log_file)
        self.mode_runner = TraversingMode(self.apk_path,self.max_retries)
        self.traversing_process  = None
        
        manager = Manager()
        self.shared_last_path = manager.Value('s', "")
        self.shared_current_retries =  manager.Value('d',max_retries)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self,sig, frame):
        # print("\Control C pressed! Save 'n Exit")
        self.mode_runner.update_status(False,"Control C pressed.")
        time.sleep(3)
        exit(0)

    def start_traversing(self):
        print("Traversing started.")
        print("APK Path: ",self.apk_path)
        self.traversing_process = multiprocessing.Process(
                target=self.mode_runner.traverse,  # Pass the function reference
                args=(self.adb_monitor.get_device_specs()['serial_number'], self.apk_path,self.retry_failed_apps),
                daemon = False
            )
        print("Traversing process created with PID: ",self.traversing_process.pid)
        self.traversing_process.start()
        print(" 2-> Traversing process created with PID: ",self.traversing_process.pid)
        self.mode_runner.shared_is_traversing_running.value = True
        

    # Stop traversing: kill traversing pid, re-initialize traversing object
    def stop_traversing(self,message):
        print("Traversing stopped.",message)
        try:
            self.mode_runner.shared_is_traversing_running.value = False
            self.mode_runner.update_status(False,message)
            if self.mode_runner.shared_traverse_pid.value:
                print("Killed traversing pid: ",self.mode_runner.shared_traverse_pid.value)
                os.kill(self.mode_runner.shared_traverse_pid.value, signal.SIGTERM)
            if self.traversing_process and self.traversing_process.is_alive():
                print("Killed pid: ",self.traversing_process.pid)
                self.traversing_process.terminate()
                self.traversing_process.join()
                self.mode_runner.shared_is_traversing_running.value = False
            
        except ProcessLookupError:
            self.logger.error(f"Process with PID not found. It may have already exited.")
        except PermissionError:
            self.logger.error(f"Permission denied: Cannot check or kill process.")
        except Exception as e:
            self.logger.error(f"An error occurred while trying to kill the process: {e}")

    def onreboot_delete_restart_frida(self):
        time.sleep(3)
        # copy frida-server to new frida-server-tmp file
        run_command(["adb","shell", "su","-c", "cp","/data/local/tmp/frida-server","/data/local/tmp/frida-server-tmp"])
        # kill pid of frida
        run_command(["adb","shell", "su","-c", "$(adb shell su -c 'ps  | grep frida-server' | awk '{print $2}')"])
        # remove old frida-server
        run_command(["adb","shell", "su","-c", "rm -f","/data/local/tmp/frida-server"])
        # copy frida-server-tmp to frida-server
        run_command(["adb","shell", "su","-c", "cp","/data/local/tmp/frida-server-tmp","/data/local/tmp/frida-server"])
        # start frida server 
        run_command(["adb","shell", "su","-c", "'nohup /data/local/tmp/frida-server > /dev/null 2>&1 &'"])
        time.sleep(3)

    def monitor_system(self):
        """Monitor ADB, Frida, and device status and capture logs if issues are detected."""
        while True:
            try:
                # Check ADB connectivity
                if self.mode_runner.traverse_ended.value:
                    break
                current_adb_status = self.adb_monitor.is_device_connected()
                if not current_adb_status:
                    if self.mode_runner.shared_is_traversing_running.value:
                        self.stop_traversing("ADB failed or device rebooted.")
                        self.mode_runner.shared_is_traversing_running.value = False
                    print("ADB is not working properly.")
                    self.adb_monitor.reconnect_device()
                    self.adb_monitor.device_info()

                # Check device status
                current_device_status = self.device_status.check_device_status()
                if not current_device_status:
                    if self.mode_runner.shared_is_traversing_running.value:
                        self.stop_traversing("Boot sequence is not yet completed.")
                        self.mode_runner.shared_is_traversing_running.value = False

                    # self.mode_runner.shared_is_traversing_running.value = False
                    # print("Boot sequence is not yet completed.")
                    bootflag = 0
                    print("Boot sequence is not yet completed--.")
                    while not self.device_status.check_device_status():
                        bootflag=1
                    time.sleep(1)
                    if bootflag == 1 :
                        self.onreboot_delete_restart_frida()
                        bootflag = 0

                # Zygote restart
                zygote_status = self.device_status.check_zygote_status()
                if not zygote_status:
                    if self.mode_runner.shared_is_traversing_running.value:
                        self.stop_traversing("Zygote is not ready--.")
                        self.mode_runner.shared_is_traversing_running.value = False
                    zygoteflag = 0
                    print("Zygote is not ready--.")
                    while not self.device_status.check_zygote_status():
                        zygoteflag=1
                    time.sleep(1)
                    if zygoteflag == 1 :
                        self.onreboot_delete_restart_frida()
                        zygoteflag = 0

                # Check Frida server status
                current_device_status = self.device_status.check_device_status()
                current_frida_status = self.frida_monitor.check_frida_status()
                print("Frida status: ",current_frida_status)
                if not current_frida_status:
                    if self.mode_runner.shared_is_traversing_running.value:
                        self.stop_traversing("Frida failed.")
                        self.mode_runner.shared_is_traversing_running.value = False
                    print("Frida is not ready--.")
                    # self.onreboot_delete_restart_frida()
                    self.frida_monitor.fix_frida()
                    self.adb_monitor.device_info()
                    time.sleep(5)

                if current_adb_status and current_frida_status and current_device_status and zygote_status:
                        if self.traversing_process:
                            if self.traversing_process.is_alive():
                                if not self.mode_runner.shared_is_traversing_running.value:
                                    time.sleep(7)
                                    continue
                            else:
                                # self.stop_traversing("")
                                self.start_traversing()
                                time.sleep(7)
                        else:
                            self.start_traversing()
                            time.sleep(7)
                time.sleep(5)
            except Exception as e:
                self.logger.info(e)
                continue

    from datetime import datetime

    def time_diff_in_seconds(self, start, end):
        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)
        return (end_time - start_time).total_seconds()

    def are_all_attempts_less_than_2_minute(self, app_data):
        if 'attempts' in app_data and len(app_data['attempts']) > 0:
            for attempt in app_data['attempts']:
                start = attempt['start_timestamp']
                end = attempt.get('end_timestamp', "")

                if end:
                    duration = self.time_diff_in_seconds(start, end)

                    if duration <= 180:
                        return True
            return False
        return False


    # Capture logs if needed
    def capture_logs(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        logcat_file = f"logcat_{timestamp}.log"
        tombstones_file = f"tombstones_{timestamp}.log"

        # Capture logcat
        try:
            with open(logcat_file, "wb") as f:
                subprocess.run(["adb", "logcat", "-d"], stdout=f, check=True)
            self.logger.info(f"Logcat saved to {logcat_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to capture logcat: {e}")

        # Capture tombstones
        try:
            with open(tombstones_file, "wb") as f:
                subprocess.run(["adb", "shell", "cat", "/data/tombstones/*"], stdout=f, check=True)
            self.logger.info(f"Tombstones saved to {tombstones_file}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to capture tombstones: {e}")

    def run(self, mode):
        """Run the application in manual or auto traversing mode."""
        try:
            

            # Start monitoring system status
            # 1. Check ADB and device status
            if not (self.adb_monitor.is_device_connected() and self.adb_monitor.device_info() ): #and self.device_status.check_device_status()
                self.logger.error("Device is not ready or connected. Aborting execution.")
                return
            
            # 2. Ensure Frida is running
            if not (self.frida_monitor.check_frida_status()): #and self.frida_monitor.test_frida_server()
                # self.frida_monitor.push_start_frida_server()
                self.frida_monitor.fix_frida()
                time.sleep(15)
            # 3. Execute mode (manual or traversisng)
            if mode == "manual":
                self.logger.info("Starting manual traversing mode...")
                # mode_runner = ManualMode(self.apk_path, log_file)
                # mode_runner.run()
            elif mode == "auto":
                self.mode_runner = TraversingMode(self.apk_path,self.max_retries)
                self.logger.info("Starting auto traversing mode...")
                
                if self.retry_failed_apps:
                    status_data = self.mode_runner.read_status_file()
                    for app_name, app_data in status_data.items():
                        if app_name in os.listdir(self.apk_path) and (app_data.get('status') == False or self.are_all_attempts_less_than_2_minute(app_data) ):
                            self.mode_runner.reset_attempts(app_name)
                self.monitor_system()

            else:
                self.logger.error("Invalid mode selected.")
        except Exception as e:
            self.logger.error(f"Application run failed: {e}", exc_info=True)
