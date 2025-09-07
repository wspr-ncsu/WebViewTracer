import subprocess as sbp
import argparse
import local_data_store
import os

def wakeup(data_directory: str):
    proc = sbp.run(['docker', 'compose', 'start'], cwd=data_directory)
    if proc.returncode != 0:
        print('Failed to wake up wvt-crawler server')
        os._exit(-1)

def system_check():
    print('Checking if system is compatible to run WebViewTracer crawler...')
    proc = sbp.run(['docker', 'info'], capture_output=True, text=True)
    if proc.returncode != 0:
        print('Docker is not installed or not found in PATH. Please install Docker from https://docs.docker.com/get-docker/')
        os._exit(-1)
    if 'podman' in proc.stdout.lower():
        print('This configuration is not supported at this time. Please install the Docker Engine. See https://docs.docker.com/engine/install/')
        os._exit(-1)

    proc = sbp.run(['docker', 'compose', 'version'], capture_output=True, text=True)
    if proc.returncode != 0:
        print('Docker Compose is not installed or not found in PATH. Please install Docker Compose from https://docs.docker.com/compose/install/')
        os._exit(-1)

    proc = sbp.run(['uname', '-m'], capture_output=True, text=True)
    if proc.returncode != 0 or 'x86_64' not in proc.stdout:
        print('This configuration is not supported at this time. Please use a Linux x86_64 system.')
        os._exit(-1)

    if os.path.exists('/dev/kvm'):
        kvm_proc = sbp.run(['ls', '-la', '/dev/kvm'], capture_output=True, text=True)
        if kvm_proc.returncode != 0 or 'crw-rw----' not in kvm_proc.stdout:
            print('KVM is not properly configured. Please ensure that /dev/kvm is accessible.')
            os._exit(-1)

    user_proc = sbp.run(['id', '-nG'], capture_output=True, text=True)
    if user_proc.returncode != 0 or 'docker' not in user_proc.stdout.split():
        print('Current user is not in the docker group. Please add the user to the docker group and re-login.')
        os._exit(-1)
    
    perm_proc = sbp.run(['docker', 'ps'], capture_output=True, text=True)
    if perm_proc.returncode != 0:
        print('Current user does not have permissions to access the docker daemon. Please ensure that the user is in the docker group and re-login.')
        os._exit(-1)

    kvm_group_proc = sbp.run(['getent', 'group', 'kvm'], capture_output=True, text=True)
    if kvm_group_proc.returncode != 0 or os.getlogin() not in [s.strip() for s in kvm_group_proc.stdout.split(':')[-1].split(',')]:
        print('Current user is not in the kvm group. Please add the user to the kvm group and re-login.')
        os._exit(-1)

    print('This system is compatible to run WebViewTracer crawler... Continuing...')

def shutdown(data_directory: str):
    proc = sbp.run(['docker', 'compose', 'stop'], cwd=data_directory)
    if proc.returncode != 0:
        print('Failed to shutdown wvt-crawler server')
        os._exit(-1)

def remove(data_directory: str):
    proc = sbp.run(['docker', 'compose', 'down'], cwd=data_directory)
    if proc.returncode != 0:
        print('Failed to remove wvt-crawler server')
        os._exit(-1)

def create(data_directory: str):
    pull_proc = sbp.run(['docker', 'pull', 'visiblev8/vv8-base:latest'], cwd=data_directory)
    if pull_proc.returncode != 0:
        print('Failed to pull latest images for visiblev8 for wvt-crawler server')
        os._exit(-1)
    up_proc = sbp.run(['docker', 'compose', '--env-file', '.env', 'up', '--build', '-d', '-V', '--force-recreate', '--remove-orphans'], cwd=data_directory, env={'COMPOSE_BAKE': "false"})
    if up_proc.returncode != 0:
        print('Failed to create wvt-crawler server')
        os._exit(-1)

def follow_logs(data_directory: str):
    proc = sbp.run(['docker', 'compose', 'logs', '-f'], cwd=data_directory)
    if proc.returncode != 0:
        print('Failed to follow logs of wvt-crawler server')
        os._exit(-1)

def docker(args: argparse.Namespace):
    data_store = local_data_store.init()
    if not (data_store.server_type == 'local'):
        print('wvt-crawler server is not running locally')
        os._exit(-1)
    if args.start:
        wakeup(data_store.data_directory)
    elif args.stop:
        shutdown(data_store.data_directory)
    elif args.rebuild:
        remove(data_store.data_directory)
        create(data_store.data_directory)
    elif args.follow_logs:
        follow_logs(data_store.data_directory)
    else:
        pass

def docker_parse_args(docker_arg_parser: argparse.ArgumentParser):
    docker_arg_parser.add_argument('-s', '--start', help='start the wvt-crawler server', action='store_true')
    docker_arg_parser.add_argument('-t', '--stop', help='stop the wvt-crawler server', action='store_true')
    docker_arg_parser.add_argument('-r', '--rebuild', help='rebuild the wvt-crawler server', action='store_true')
    docker_arg_parser.add_argument('-f', '--follow-logs', help='follow the logs of the wvt-crawler server', action='store_true')
