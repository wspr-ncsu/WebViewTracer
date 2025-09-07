import os
import argparse
import pathlib

parser = argparse.ArgumentParser(
                    prog='Play Store Downloader',
                    description='Downloads apps from Play Store')
parser.add_argument('directory', metavar='DIR', type=pathlib.Path,
                    help='A directory to save the apps')
parser.add_argument('list', metavar='LIST', type=ascii,
                    help='A list of apps')

args = parser.parse_args()

saved_apps_dir = args.directory
app_list = args.list.replace("'","")

with open(app_list) as f:
        for line in f:
                apk = line.replace("\n", "")
                print(apk)
                try:
                        error=os.popen(f"java -Draccoon.homedir={saved_apps_dir} -Draccoon.home={saved_apps_dir}/apps/ -jar raccoon-4.24.0.jar --gpa-download {apk}").read().replace("\n","")
                        if error=="!fail.Item not found.!":
                                print(f"Error: app with package name {apk} not found in PlayStore.")
                                os.system(f"echo {apk} >> notFound")
                        elif "DF-DFERH-" in error:
                                print(f"Error: app with package name {apk} not downloaded.")
                                os.system(f"echo {apk} >> notDownloaded")
                        print(error)
                except e:
                        print("exception")