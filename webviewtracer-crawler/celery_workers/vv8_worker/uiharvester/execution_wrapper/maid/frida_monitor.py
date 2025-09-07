import logging,subprocess,frida,time,psutil,sys,os
from pathlib import Path
from utils.command_exec import frun_command,try_command,run_command

import traceback
class FridaMonitor:
    def __init__(self, log_file):
        self.logger = logging.getLogger('FridaMonitor')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.current_dir = Path(__file__).parent
    
    def on_message(self):
        self.logger.info("Hook's working")
    
    def is_frida_crashed(self):
        try:
            not_crashed =  ["frida-ps -U"]
            result = subprocess.run(not_crashed, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,timeout=7)
            #print("Frida-ps -U result: ",result.stdout)
            #print("Frida-ps -U error: ",result.stderr)
            if result.returncode == 0:

                return False
        except Exception as e:
            print("Frida crashed",e)
            return True
        return True

    # Function to check Frida server status
    def is_frida_server_running(self):
        try:
            # Try getting the device list to check if Frida server is reachable
            pid = run_command(["adb","shell","su","-c","pidof","frida-server"])
            if pid:return pid
            else: return False
        except frida.ServerNotRunningError:
            self.logger.error("Frida server is not running.")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return False
        
    def check_frida_status(self):
        pid = self.is_frida_server_running()
        print("Frida PID: ",pid)
        print("Are we stuck here?")
        if not pid: return False
        return not self.is_frida_crashed()
    
    # Simple frida script to test server status
    def test_frida_server(self):
        try:
            device = frida.get_usb_device(timeout=5)
            pid = device.spawn(['com.google.android.calculator'])
            session = device.attach(pid)
            script = session.create_script("""
                Java.perform(function() {
                    var Activity = Java.use('android.app.Activity');
                    Activity.onResume.implementation = function() {
                        send('onResume called');
                        this.onResume();
                    };
                });
            """)
            script.on('message', self.on_message)
            # Load and run the script
            script.load()
            # Unload the script and detach from the app
            script.unload()
            session.detach()
            time.sleep(2)
            subprocess.run(["adb", "shell", "am", "force-stop", 'com.google.android.calculator'], check=True)
            return True
        except :
            return False
            
    def get_device_architecture(self):
        """Get the CPU architecture of the Android device."""
        arch_map = {
            "armeabi": "arm",
            "armeabi-v7a": "arm",
            "arm64-v8a": "arm64",
            "x86": "x86",
            "x86_64": "x86_64"
        }
    #     arch_map = {
    #     "armeabi": "arm",
    #     "armeabi-v7a": "arm",
    #     "arm64-v8a": "arm64",
    #     "x86": "x86",
    #     "x86_64": "x86_64",
    #     "mips": "mips",
    #     "mips64": "mips64",
    #     "riscv64": "riscv64",  # Adding potential RISC-V architecture
    # }
        
        # Build the ADB getprop command
        getprop_cmd = ["adb", "shell", "getprop", "ro.product.cpu.abi"]
        
        try:
            # Run the command without using shell=True
            output = subprocess.check_output(getprop_cmd, stderr=subprocess.STDOUT).lower().strip().decode("utf-8")
            
            # Determine the architecture
            arch = arch_map.get(output, None)
            
            return arch
        
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to get architecture. {e}")
            return None
    
    def clean_frida(self):
        pid = self.is_frida_server_running()
        if pid:
            # Kill the frida-server process using its PID
            kill_command = ["adb","shell","su","-c","kill","-9",pid]
            kill_result = run_command(kill_command)
        try:
            remove_command = ["adb","shell","su","-c","rm","-f","/data/local/tmp/frida-server"]
            run_command(remove_command)
        except:print("Frida binary does not exist")
        # fridaArc = run_command(["adb","shell","getprop","ro.product.cpu.abi"]).split('-')[0]
        
        fridaArc = self.get_device_architecture()
        fridaVer = run_command(["frida","--version"])

        if not fridaArc or not fridaVer:
            return "Error: Could not determine CPU architecture or Frida version."

        # Download Frida server
        fridaServerUrl = f"https://github.com/frida/frida/releases/download/{fridaVer}/frida-server-{fridaVer}-android-{fridaArc}.xz"
        print("Downloading: ",fridaServerUrl)
        
        download_command = ["wget",fridaServerUrl,"-P","utils/","-O","utils/frida-server.xz",">","/dev/null","2>&1"]
        run_command(download_command)
        time.sleep(5)
        # Uncompress the downloaded file
        uncompress_command = ["unxz","utils/frida-server.xz"]
        run_command(uncompress_command)
        time.sleep(5)        
        print("Cleaning previous frida-server failed.")

    def push_frida(self):
        print("Pushing Frida server to device.")
        traceback.print_stack()
        process_push = subprocess.Popen(['adb','push','/app/frida-server',"/data/local/tmp"], text=True,cwd=self.current_dir.parent)
        time.sleep(5)
        process_chmod = subprocess.Popen(["adb","shell", "su","-c", "chmod","0755","/data/local/tmp/frida-server"], text=True,cwd=self.current_dir.parent)

    def start_frida(self):
        run_command(["adb","shell", "su","-c", "'setenforce 0'"])
        run_command(["adb","shell", "su","-c", "'nohup /data/local/tmp/frida-server > /dev/null 2>&1 &'"])

    # Recovery function to restart Frida server
    def fix_frida(self):
        # Attempting to fix Frida server.

        if self.is_frida_crashed():
            self.clean_frida()
            self.push_frida()
            self.start_frida()
            time.sleep(10)
        else:
            
            pid = self.is_frida_server_running()
            if not pid:
                command = ["adb","shell", "su","-c","ls", "/data/local/tmp/frida-server"]
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "No such file or directory" in result.stderr:
                    print("Frida server does not exist in device.")
                    self.clean_frida()
                    self.push_frida()
                self.start_frida()
            else:
                print("frida process alive and frida-ps -U working")
            time.sleep(5)
        time.sleep(5)
        # pid = run_command(["adb","shell", "su","-c","pidof frida-server"])
        # if pid:
        #     res = run_command(["adb","shell", "su","-c",f"kill -9 {pid}"])
        #     print(res)

        # print("Killing PID of frida-server - Initializing frida-server.")
        # # copy frida-server to new frida-server-tmp file
        # run_command(["adb","shell", "su","-c", "cp","/data/local/tmp/frida-server","/data/local/tmp/frida-server-tmp"])
        # # kill pid of frida
        # run_command(["adb","shell", "su","-c", "$(adb shell su -c 'ps  | grep frida-server' | awk '{print $2}')"])
        # # remove old frida-server
        # run_command(["adb","shell", "su","-c", "rm -f","/data/local/tmp/frida-server"])

        # waitingfrida=15;print("Waiting",waitingfrida,"seconds to restart frida-server.");time.sleep(waitingfrida)
        
        # # copy frida-server-tmp to frida-server
        # run_command(["adb","shell", "su","-c", "cp","/data/local/tmp/frida-server-tmp","/data/local/tmp/frida-server"])
        # # start frida server 
        # papa = run_command(["adb","shell", "su","-c", "'nohup /data/local/tmp/frida-server > /dev/null 2>&1 &'"])
        # time.sleep(10)

    
    def detect_frida_processes(self):
        frida_keywords = ["frida", "agent", "gum"]
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if any(keyword in ' '.join(proc.info['cmdline']) for keyword in frida_keywords):
                logging.warning(f"frida process detected: {proc.info['name']} with command: {' '.join(proc.info['cmdline'])}")
                return True
        return False

    # Detect frida pipes 
    def detect_frida_pipes(self):
        try:
            # List pipes in /proc/<pid>/fd for each process
            for proc in psutil.process_iter(['pid']):
                pid = proc.info['pid']
                fd_dir = f"/proc/{pid}/fd"
                if os.path.exists(fd_dir):
                    for fd in os.listdir(fd_dir):
                        try:
                            pipe_target = os.readlink(os.path.join(fd_dir, fd))
                            if "pipe" in pipe_target and "frida" in pipe_target:
                                logging.warning(f"frida pipe detected in process {pid}: {pipe_target}")
                                return True
                        except OSError:
                            continue
        except Exception as e:
            logging.error(f"Error detecting frida pipes: {e}")
        return False

    # Detect frida executable segments
    def detect_frida_segments(package_name):
        try:
            # Get the PID of the app
            pid = subprocess.check_output(["adb", "shell", "pidof", package_name]).decode().strip()
            if pid:
                # Use `adb shell cat /proc/<pid>/maps` to check memory segments
                maps_output = subprocess.check_output(["adb", "shell", f"cat /proc/{pid}/maps"]).decode()
                for line in maps_output.splitlines():
                    if "r-xp" in line and "/data/local/tmp" in line:
                        logging.warning(f"frida executable segment detected: {line}")
                        return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error detecting frida segments: {e}")
        return False