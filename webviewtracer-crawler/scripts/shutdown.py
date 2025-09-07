import os
import local_data_store
import docker

def shutdown():
    """
    Shutdown the WebViewTracer crawler gracefully.
    """
    print("Shutting down WebViewTracer crawler...", flush=True)
    local_data_storage = local_data_store.init()
    for service in range(1, local_data_storage.number_of_phones + 1):
        print(f"Stopping service {service}...", flush=True)
        os.system(f"docker compose exec -u 0 vv8_worker_{service} adb shell reboot -p")
    print("All services stopped. Waiting for 10 seconds...", flush=True)
    os.system("sleep 10")
    docker.shutdown(local_data_storage.data_directory)
    print("WebViewTracer crawler shutdown complete.", flush=True)