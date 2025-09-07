import os
import time, logging
from multiprocessing import Manager,Array
import subprocess,json
from datetime import datetime
from utils.command_exec import frun_command, run_command

class TraversingMode:
    def __init__(self, apk_path, max_retries,):
        self.apk_path = apk_path
        log_file = f"/app/logs/traversing.log"
        self.logger = logging.getLogger('Traversing')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        # self.successful_log = "logs/successful_traversals.log"
        self.unsuccessful_log = "/app/logs/unsuccessful_traversals.log"
        
        manager = Manager()
        self.shared_last_path = manager.Value('s', "Start")
        self.shared_is_traversing_running = manager.Value('b', False)
        self.shared_traversal_start_time = manager.Value('s', "")
        self.max_retries =  max_retries
        self.shared_current_retries =  manager.Value('i',max_retries)
        self.traverse_ended = manager.Value('b',False)
        self.shared_traverse_pid = manager.Value('i',None)

        self.status_file = "/app/logs/traversal_status.json"
        if not os.path.exists(self.status_file):
            self.initialize_status_file()

                  
    def initialize_status_file(self):
        """Create a new JSON file to track traversal status."""
        status_data = {}
        with open(self.status_file, 'w') as file:
            json.dump(status_data, file)

    def read_status_file(self):
        """Read the JSON file and return its contents."""
        if not os.path.exists(self.status_file):
            self.initialize_status_file()
        
        try:
            with open(self.status_file, 'r') as file:
                return json.load(file)
        except:
            self.initialize_status_file()
            with open(self.status_file, 'r') as file:
                return json.load(file)
    
    def init_app_record(self,app_name):
        status_data = self.read_status_file()
        if app_name not in status_data:
            status_data[app_name] = {'attempts': [], 'status': False}
        with open(self.status_file, 'w') as file:
            json.dump(status_data, file, indent=4)

    def reset_attempts(self,app_name):
        status_data = self.read_status_file()
        if app_name in status_data:
            del status_data[app_name]  # Delete the app entry from the dictionary
        # Write the updated data back to the JSON file
        with open(self.status_file, 'w') as file:
            json.dump(status_data, file, indent=4)

    def update_attempt(self, app_name):
        """
        Update the attempts array of a given app in the JSON file.
        
        Args:
            app_name (str): Name of the application to update.
            result (str): The result of the attempt (e.g., 'Success', 'Failed').
        """
        status_data = self.read_status_file()

        if app_name not in status_data:
            status_data[app_name] = {'attempts': [], 'status': False}
        
        # Append the new attempt result with timestamp
        attempt_record = {
            'start_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'end_timestamp': ""
        }
        status_data[app_name]['attempts'].append(attempt_record)

        # Write back to the JSON file
        with open(self.status_file, 'w') as file:
            json.dump(status_data, file, indent=4)

    def update_status(self, status,message):
        """
        Update the status of the last app that has not reached the max retries and does not have status `True`.
        
        Args:
            status (str): The new status to set for the application.
            max_retries (int): Maximum number of retries allowed for each application.
        """
        status_data = self.read_status_file()
        
        # Find the last app that has attempts < max_retries and status != True
        app_name = None
        for app in status_data.keys():
            app_info = status_data[app]
            attempts = app_info.get('attempts', [])
            current_status = app_info.get('status', False)
            
            if len(attempts) < self.max_retries and current_status != True :
                app_name = app
                break

            if len(attempts) == self.max_retries and any(len(attempt) != 4 for attempt in attempts) and current_status != True :
                app_name = app
                break

        if not app_name:
            self.logger.error("No application found with attempts less than max_retries and status not True.")
            return
        
        # Update the status and end timestamp for the last attempt of the found app
        status_data[app_name]['status'] = status
        if status_data[app_name]['attempts']:
            status_data[app_name]['attempts'][-1]['end_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_data[app_name]['attempts'][-1]['status'] = status
        else:
            # If no attempts exist, add a new one with an end timestamp
            self.update_attempt(app_name)
            status_data[app_name]['attempts'][-1]['end_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_data[app_name]['attempts'][-1]['status'] = status
        if not status:
            status_data[app_name]['attempts'][-1]['message'] = message
        # Write back to the JSON file
        with open(self.status_file, 'w') as file:
            json.dump(status_data, file, indent=4)    

    def log_successful_traversal(self, app):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.shared_traversal_start_time and self.shared_traversal_start_time.value == "":
            with open(self.successful_log, 'a') as f:
                f.write(f" - ,{timestamp},{app}\n")
        else:
            with open(self.successful_log, 'a') as f:
                f.write(f"{self.shared_traversal_start_time.value},{timestamp},{app}\n")

    def log_unsuccessful_traversal(self, app, error_message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.shared_traversal_start_time and  self.shared_traversal_start_time.value == "":
            with open(self.unsuccessful_log, 'a') as f:
                f.write(f" - ,{timestamp},{app},{error_message}\n")
        else:
            with open(self.unsuccessful_log, 'a') as f:
                f.write(f"{self.shared_traversal_start_time.value},{timestamp},{app},{error_message}\n")
    def daemon_is_not_running(self):
        try:
            result = subprocess.run(
                ["adb", "shell", "su", "-c", "ps | grep 'daemon_name'"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return "No daemon" in result.stdout
        except Exception as e:
            self.logger.error(f"Error checking daemon status: {e}")
            return True
        
    def run_frida_script(self, app, serialnum):
        # Open tailscale to make sure our vpn is working
        os.system("adb shell am start -n com.tailscale.ipn/com.tailscale.ipn.MainActivity > /dev/null 2>&1")
        time.sleep(5)
        print("Running frida script", flush=True)
        frida_cmd = [
            "python3", "-u", "traversing.py",
            "-p", app,
            "-d", serialnum,
            "-e","BFS",
            "-o",app,
            "-c","1",
            "-s","2",
            "-a","5",
            "-G","1",
            "-t","300",
            "-w","1",
            #"-fl","frida-scripts/sslunpinning.js"
            # "-fl","frida-scripts/sslunpinning.js","frida-scripts/hook_android_classmethod.js"
        ]
        parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # if not self.retry_command(frida_cmd, cwd=parent_directory):
        #     self.logger.error(f"Failed to run Frida script for app {app}")
        #     return False
        # self.shared_traversal_start_time.value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.update_attempt(app)
        print(frida_cmd)

        # AAAAHHHHHHHHHH!
        os.system('/app/nuke.sh')
        print("Nuked", flush=True)
        process = subprocess.Popen(frida_cmd, cwd=parent_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # self.logger.info(f"Attempt {int(self.shared_current_retries.value) + 1}: Running command {frida_cmd} with PID {process.pid}")
        self.shared_traverse_pid.value = process.pid

        # Read output from the command while it is running
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:  # Check if the process has finished
                break
            if output:  # If there is output, print it
                print(output.strip(), flush=True)  # Print each line of output as it is generated

        stdout, stderr = process.communicate()  # Make sure all output has been collected

        #os.system("adb reboot")
        #time.sleep(60)

        if process.returncode == 0 : # and self.shared_is_traversing_running.value
            
            return True
            # self.shared_current_retries.value = self.max_retries
        else: 
            
            return False
            # else:
                # self.shared_current_retries.value -= 1
                # self.logger.error(f"Attempt {int(self.shared_current_retries.value) + 1} failed for command {cmd} with PID {process.pid}: {stderr}")
        # except subprocess.CalledProcessError as e:
            # self.shared_current_retries.value -= 1
            # self.logger.error(f"Attempt {int(self.shared_current_retries.value) + 1} failed for command {cmd}: {e}")

        # self.shared_current_retries.value = self.max_retries -1
        # self.shared_last_path.value = None
        # except Exception as e:
        #     print(e)
        #     return False
        
        return True
    def install_multiple_apks(self, path2, apks):
        try:
            
            package_name = path2.split('/')[-1]
            #self.init_app_record(package_name)
            #Uninstall any existing installation
            uninstall_cmd = ["adb", "uninstall", package_name]
            uninstall_process = subprocess.Popen(uninstall_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = uninstall_process.communicate()
            
            if uninstall_process.returncode == 0:
                print(f"Successfully uninstalled existing installation of {package_name}.")
            else:
                print(f"No existing installation found for {package_name} or failed to uninstall.")
            
            # Proceed with installation
            print(f"Installing application from {path2}...")
            self.logger.info(f"Installing APKs from {path2}...")
            self.shared_is_traversing_running.value = True
            # while True:
            #     output = run_command(["adb","shell", "su","-c","getprop","sys.boot_completed"])
            #     if output == '1':
            #         zygote64 = run_command(["adb","shell", "su","-c","ps","|","grep","zygote64"])
            #         if zygote64:
            #             break
            install_cmd = ["adb", "install-multiple", "-g"] + [os.path.join(path2, apk) for apk in apks if apk.endswith(".apk")]
            install_process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = install_process.communicate()
            
            if install_process.returncode == 0:
                print(f"Successfully installed application from {path2}.")
                return True
            else:
                print(f"Failed to install application from {path2}. Error: {stderr.decode()}")
                install_cmd = ["adb", "install", "-g"] + [os.path.join(path2, apk) for apk in apks if package_name in apk]
                install_process = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = install_process.communicate()
                if install_process.returncode == 0:
                    print(f"Successfully installed application from {path2}.")
                    return True
                else:
                    print(f"Failed to install application from {path2}. Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"An error occurred during the installation process: {e}")
            return False
        except Exception as e:
            print(f"An error occurred during the installation process: {e}")
            return False
        return True

    def uninstall_stuff(self,app):
        os.system("adb shell su -c \"input keyevent KEYCODE_HOME\" > /dev/null 2>&1")
        time.sleep(1)
        os.system("adb shell su -c \"input keyevent KEYCODE_HOME\" > /dev/null 2>&1")
        time.sleep(1)
        os.system("adb shell pm clear "+app+"  > /dev/null 2>&1")
        os.system("ps aux | grep -i \"adb logcat\" | grep -v \"grep\" | awk '{print \"kill -9 \"$2}' | bash  > /dev/null 2>&1")
        os.system("adb shell logcat -b all -c  > /dev/null 2>&1")

        os.system("adb shell \" su -c 'service call notification 1'\" > /dev/null 2>&1")
        os.system("adb uninstall "+ app+" > /dev/null 2>&1")
    
    def clear_app_data(self,folder):
        try:
            frun_command(["adb","shell", "su","-c", "pm", "clear", folder, " > /dev/null 2>&1"])
            frun_command(["adb", "shell", "logcat", "-b", "all", "-c", " > /dev/null 2>&1"])
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to clear app data or logs: {e}")

    def traverse(self, serialnum, apps_path, retry_failed_apps):
        try:
            """Main traversal logic."""
            print("About to list directories in apps_path:", apps_path)
            folders = os.listdir(apps_path)

            print(f"Found {len(folders)} folders in {apps_path}.")
            
            if not folders:
                print("App folder empty.")
                return
            
            for folder in folders:
                
                status_data = self.read_status_file()
                path2 = os.path.join(apps_path, folder)
                app = folder.split("/")[-1]
                
                if app in status_data and len(status_data[app]['attempts']) >= self.max_retries:
                    print(f"Skipping {app} as it has reached max retries.")
                    continue
                if app in status_data and  status_data[app]['status']:
                    print(f"Skipping {app} as it has been previously traversed.")
                    continue
                    
                apks = os.listdir(os.path.join(apps_path, folder))
                
                time.sleep(1)
                if not os.path.exists(path2) :
                    print("os.path.exists(path2)")
                    self.logger.error(f"{path2} not found")
                    continue

                if not apks:
                    self.logger.info(f"No apk(s) found in {path2}")
                    self.log_unsuccessful_traversal(folder, "No .apk(s) found.")
                    continue
                
                if not self.install_multiple_apks(path2, apks):
                    self.log_unsuccessful_traversal(folder, "Installation failed.")
                    self.init_app_record(app)
                    continue
                
                print(f"Traversing app {folder}...")

                trial = self.run_frida_script(folder, serialnum)
                os.system("adb shell su -c \"input keyevent KEYCODE_HOME\" > /dev/null 2>&1")
                time.sleep(1)
                os.system("adb shell su -c \"input keyevent KEYCODE_HOME\" > /dev/null 2>&1")
                time.sleep(1)
                os.system("adb shell pm clear "+folder+"  > /dev/null 2>&1")
                os.system("ps aux | grep -i \"adb logcat\" | grep -v \"grep\" | awk '{print \"kill -9 \"$2}' | bash  > /dev/null 2>&1")
                os.system("adb shell logcat -b all -c  > /dev/null 2>&1")

                os.system("adb shell \" su -c 'service call notification 1'\" > /dev/null 2>&1")
                os.system("adb uninstall "+ folder+" > /dev/null 2>&1")

                self.clear_app_data(path2)
                
                if self.shared_current_retries.value >= 0 and trial:
                    self.update_status(True,"")
                if self.shared_current_retries.value < 0 and not trial:
                    self.update_status(False,"Max retries.")
                if self.daemon_is_not_running():
                    self.logger.error("Daemon is not running!")
                    os.system("adb reboot")
                    return
                
            self.traverse_ended.value = True

        except Exception as e:
            # self.shared_is_traversing_running.value = True
            print(e)
            # self.log_unsuccessful_traversal(folder,f"Failed run: {e}")
            return False
        return True
