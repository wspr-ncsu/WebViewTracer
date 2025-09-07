import argparse
from pathlib import Path
from typing import Tuple
import local_data_store
import os
import re
import time
from rich.prompt import Prompt, IntPrompt
import docker
import subprocess as sbp
import shutil
import sys
from dotenv import load_dotenv

load_dotenv()

def setup(args: argparse.Namespace):
    url = 'http://192.168.0.1:4000'
    server_type = None
    instance_count = 1
    number_of_phones = 1
    if args.local:
        (url, server_type, instance_count, number_of_phones) = setup_local()
    else:
        type = Prompt.ask('Do you want to setup WebViewTracer completely locally, or have WebViewTracer connect to remote databases?',
                              choices=['local', 'connect'], default='local')
        if type == 'local':
            (url, server_type, instance_count, number_of_phones) = setup_local()
        elif type == 'connect':
            (url, server_type, instance_count, number_of_phones) = setup_local(connect_db=True)
    local_data_store.setup(url, server_type, instance_count, number_of_phones)

def get_all_usb_devices_with_serial():
    try:
        lsusb_output = sbp.check_output(["lsusb"]).decode("utf-8")
        pattern = r"Bus (\d{3}) Device (\d{3}): ID (\w{4}):(\w{4})"
        matches = re.finditer(pattern, lsusb_output)
        
        devices = []
        
        for match in matches:
            bus_id = match.group(1)
            device_id = match.group(2)
            vendor_id = match.group(3)
            product_id = match.group(4)
            
            try:
                detailed_output = sbp.check_output(["lsusb", "-s", f"{bus_id}:{device_id}", "-v"]).decode("utf-8")
                serial_match = re.search(r"iSerial\s+\d+\s(.+)$", detailed_output, re.MULTILINE)
                serial = serial_match.group(1) if serial_match else "N/A"
            except sbp.CalledProcessError:
                serial = "Error"
            
            devices.append({
                "bus_id": bus_id,
                "device_id": device_id,
                "vendor_id": vendor_id,
                "product_id": product_id,
                "serial": serial
            })
        
        return devices
    
    except sbp.CalledProcessError:
        print("Error running lsusb command")
        return []

def get_adb_devices():
    try:
        result = sbp.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        devices = []
        for line in lines[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) == 2 and parts[1] == 'device':
                    devices.append(parts[0])
        
        return devices
    except sbp.CalledProcessError as e:
        print(f"An error occurred while running adb: {e}")
        return []
    except FileNotFoundError:
        print("adb command not found. Make sure adb is installed and in your PATH.")
        return []

def get_correlated_devices():
    usb_devices = get_all_usb_devices_with_serial()
    adb_devices = get_adb_devices()
    correlated_devices = []
    for usb_device in usb_devices:
        for adb_device in adb_devices:
            if usb_device['serial'] == adb_device:
                correlated_devices.append(usb_device)
    return correlated_devices

def generate_device_config(devices, app_directory):
    docker_config_tmpl = open('docker-compose-app.yaml.tmpl', 'r').read()
    docker_config = open('docker-compose.build.yaml', 'r').read() + '\n'
    count = 0
    android_dir = os.path.expanduser("~/.android")
    os.makedirs("./crawl_data", exist_ok=True)
    os.system("rm -rf /tmp/.vv8-android-*")

    ports = 8555
    scrports1 = 5038
    scrports2 = 27184
    for device in devices:
        count += 1
        ports = ports + 1
        scrports1 = scrports1 + 1
        scrports2 = scrports2 + 1
        shutil.copytree(android_dir, f"/tmp/.vv8-android-{count}/")
        tmp_android_dir = f"/tmp/.vv8-android-{count}"
        bad_data_dir = os.path.abspath( os.path.join("./crawl_data", f"data-{count}") )
        shutil.copytree(android_dir, f"{tmp_android_dir}/")
        actual_config = docker_config_tmpl.replace("$SERIAL", device['serial'])
        actual_config = actual_config.replace("$ID", str(count))
        actual_config = actual_config.replace("$APP_DIRECTORY", app_directory + f"/split_{count}" )
        actual_config = actual_config.replace("$USER_ANDROID_DIR", tmp_android_dir)
        actual_config = actual_config.replace( "$ADB_PORT", str(ports) )
        actual_config = actual_config.replace( "$BAD_DATA_DIR", bad_data_dir )
        actual_config = actual_config.replace( "$SCRCPYPORT1", str(scrports1) )
        actual_config = actual_config.replace( "$SCRCPYPORT2", str(scrports2) )
        docker_config += actual_config + '\n'
        os.system(f"adb -s {device['serial']} shell su -c 'rm -rf /sdcard/Documents/*'")
        os.system(f"adb -s {device['serial']} shell su -c 'pm clear com.google.android.webview'")
    open('docker-compose.override.yaml', 'w').write(docker_config)

def create_virtual_device_docker(app_directory: str):
    docker_config_tmpl = open('docker-compose-avd.yaml.tmpl', 'r').read()
    docker_config = open('docker-compose.build.yaml', 'r').read() + '\n'
    print('At this moment, only a single virtual device is supported, to use multiple devices use physical devices')
    count = 1
    try:
        kvm_gid = int(sbp.check_output(['getent', 'group', 'kvm']).decode('utf-8').split(':')[2])
    except Exception as e:
        print(f"Error getting KVM group ID: {e}, unable to create virtual device docker")
        sys.exit(1)
    bad_data_dir = os.path.abspath( os.path.join("./crawl_data", f"data-{count}") )
    os.makedirs(bad_data_dir, exist_ok=True, mode=0o777)
    actual_config = docker_config_tmpl.replace("$ID", str(count))
    actual_config = actual_config.replace( "$BAD_DATA_DIR", bad_data_dir )
    actual_config = actual_config.replace("$APP_DIRECTORY", app_directory )
    actual_config = actual_config.replace( "$HOST_KVM_GID", str(kvm_gid) )
    docker_config += actual_config + '\n'
    open('docker-compose.override.yaml', 'w').write(docker_config)

def setup_local(connect_db=False):
    print('stopping any running containers')
    os.system("docker compose down")
    instance_count = Prompt.ask('How many instances of postprocessors do you want to run?', default=f'{os.cpu_count() * 4}')
    if not os.environ.get('APP_DIRECTORY'):
        app_directory = Prompt.ask('Which directory will you put your apps in?', default=os.path.join(os.getcwd(), 'apps'))
    else:
        app_directory = os.environ.get('APP_DIRECTORY')
    print('NOTE: Only a single virtual device is supported at this moment')
    device_type = Prompt.ask('What type of devices are you using?', choices=['physical', 'virtual'], default='virtual')
    number_of_phones = 1
    if device_type == 'virtual':
        app_dir = os.path.abspath(app_directory + '/split_1')
        os.makedirs(app_dir, exist_ok=True, mode=0o777)
        #os.chmod(app_dir, 0o777)
        create_virtual_device_docker(app_dir)
        print('setting up virtual device docker')
    else:
        print('setting up local server')
        print('correlating usb and adb devices')
        correlated_devices = get_correlated_devices()
        print(f'found {len(correlated_devices)} android devices')
        number_of_phones = len(correlated_devices)
        if number_of_phones == 0:
            print("No devices found. Make sure you have Android devices connected and adb installed.")
            os._exit(-1)
        generate_device_config(correlated_devices, app_directory)
        devices = get_adb_devices()
        if not devices:
            print("No devices found. Make sure you have Android devices connected and adb installed.")
            #os._exit(-1)
        print("Disabling adb server on host")
        os.system("adb kill-server")
    sbp.run(['make', 'docker'], cwd='./celery_workers/visiblev8/post-processor')
    if not os.path.exists('parsed_logs'):
        os.mkdir('parsed_logs', mode=0o777)
        os.chmod('parsed_logs', 0o777)
    else:
        assert oct(os.stat('parsed_logs').st_mode)[-3:] == '777', 'parsed_logs directory exists but does not have 777 permissions'
    if not os.path.exists('screenshots'):
        os.mkdir('screenshots', mode=0o777)
        os.chmod('screenshots', 0o777)
    else:
        assert oct(os.stat('parsed_logs').st_mode)[-3:] == '777', 'parsed_logs directory exists but does not have 777 permissions'
    if not os.path.exists('har'):
        os.mkdir('har', mode=0o777)
        os.chmod('har', 0o777)
    else:
        assert oct(os.stat('har').st_mode)[-3:] == '777', 'har directory exists but does not have 777 permissions'
    if not os.path.exists('raw_logs'):
        os.mkdir('raw_logs', mode=0o777)
        os.chmod('raw_logs', 0o777)
    else:
        assert oct(os.stat('raw_logs').st_mode)[-3:] == '777', 'raw_logs directory exists but does not have 777 permissions'
    connect_config = {}
    time.sleep(1)
    setup_remote_now = 'n'
    if connect_db:
        setup_remote_now = Prompt.ask('Do you want to setup connection to remote databases now? (y/n)', choices=['y', 'n'], default='y')
    if connect_db and setup_remote_now == 'y':
        print('setting up connection to remote databases')
        print('configuring PostgreSQL server:')
        connect_config['SQL_HOST'] = Prompt.ask('    Hostname:')
        connect_config['SQL_USER'] = Prompt.ask('    Username:')
        connect_config['SQL_PASSWORD'] = Prompt.ask('   Password:')
        connect_config['SQL_PORT'] = IntPrompt.ask('    Port:', default=5432)
        connect_config['SQL_DATABASE'] = Prompt.ask('    Database name:')
    elif setup_remote_now == 'n' and connect_db:
        print('Please remember to fill in the .env file before running the crawler')
    write_env(instance_count, connect_config)
    return ('0.0.0.0', 'local', instance_count, number_of_phones)

def write_env(instance_count, connect_config):
    env_file = open('.env', 'w+')
    env_file.write(f'CELERY_CONCURRENCY={instance_count}')
    if connect_config:
        env_file.write(f"\nSQL_HOST={connect_config.get('SQL_HOST') or 'database'}")
        env_file.write(f"\nSQL_USER={connect_config.get('SQL_USER') or 'vv8'}")
        env_file.write(f"\nSQL_PASSWORD={connect_config.get('SQL_PASSWORD') or 'vv8'}")
        env_file.write(f"\nSQL_PORT={connect_config.get('SQL_PORT') or '5432'}")
        env_file.write(f"\nSQL_DATABASE={connect_config.get('SQL_DATABASE') or 'vv8_backend'}")
        env_file.write(f"\nSQL_DB={connect_config.get('SQL_DATABASE') or 'vv8_backend'}")
    env_file.close()

def setup_parse_args(setup_arg_parser: argparse.ArgumentParser):
    setup_arg_parser.add_argument('-l', '--local', help='setup wvt cli and crawler to use local server', action='store_true')
