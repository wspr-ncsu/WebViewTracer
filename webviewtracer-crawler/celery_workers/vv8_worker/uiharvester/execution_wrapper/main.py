import argparse,os,json
from application_runner.runner import ApplicationRunner
status_file = "/app/logs/traversal_status.json"

def main():
    def print_stats():
        try:
            with open(status_file, 'r') as file:
                app_data =  json.load(file)
                total_apps = len(app_data)
                successful_apps = sum(1 for app in app_data.values() if app['status'])
                print(successful_apps ,"from", total_apps ,"apps ran successfully.")
                print("If you want to run failed traversals again try running with arg -retryFailedApps")
                print(f"python3 main.py -p {args.apks_path} -m {args.mode} -r {args.max_retries} -retryFailedApps")
        except Exception as e:
            print(e,"Reading stats failed.")
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run an application with the ApplicationRunner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Shows default values in help
    )
    
    # Add arguments
    parser.add_argument('-p', '--apks-path', type=str, required=True, help='Path to the APK directory')
    parser.add_argument('-m', '--mode', type=str, choices=['manual', 'auto'], required=True, help='Mode to run: "manual" or "auto"')
    parser.add_argument('-r', '--max-retries', type=int, default=3, help='Maximum number of retries (default: 3)')
    parser.add_argument('-retryFailedApps', '--retry-Failed-Apps', action='store_true', help='Retry traversing apps from an old run.')


    # Parse arguments
    args = parser.parse_args()
    # Create an ApplicationRunner instance
    runner = ApplicationRunner(args.apks_path,max_retries=args.max_retries,retry_failed_apps=args.retry_Failed_Apps ) #scripts=args.frida_scripts

    # Run the application in the specified mode with max retries and Frida scripts
    runner.run(args.mode)
    print_stats()


if __name__ == "__main__":
    main()
    
