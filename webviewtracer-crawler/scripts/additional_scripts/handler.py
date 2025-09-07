from collections import defaultdict
from tqdm.notebook import tqdm
import numpy as np
import pandas as pd
from tasks import process_fingerprinting_batch

# Database connection (Modify credentials as needed)
DB_CONFIG = dict(
    database="vv8_backend",
    host="0.0.0.0",
    user="vv8",
    password="vv8",
    port="5439"
)

BATCH_SIZE = 1000

def fetch_and_process_parallel(package_names, total_scripts):
    """
    Fetches and processes data in parallel batches using Celery.
    Aggregates the results into a dictionary mapping apps to their
    unique fingerprinting APIs.
    """
    offsets = range(0, total_scripts, BATCH_SIZE)

    tasks = [
        process_fingerprinting_batch.delay(package_names, offset, BATCH_SIZE)
        for offset in offsets
    ]

    app_fingerprinting_data = defaultdict(set)

    for task in tqdm(tasks, desc="Processing batches"):
        result = task.get()
        for app, api_set in result.items():
            app_fingerprinting_data[app].update(api_set)

    return app_fingerprinting_data

def run_single_pass(whitelisted_apps):
    """Processes all scripts for whitelisted apps in one run, in batches."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM script_flow
        WHERE package_name = ANY(%s)
    """, (whitelisted_apps,))
    total_scripts = cur.fetchone()[0]

    cur.close()
    conn.close()

    if total_scripts == 0:
        print("No fingerprinting scripts found for the whitelisted apps.")
        return {}

    print(f"Processing {total_scripts} scripts in batches of {BATCH_SIZE}...")

    app_fingerprinting_data = fetch_and_process_parallel(whitelisted_apps, total_scripts)

    app_unique_api_counts = app_fingerprinting_data
    #app_unique_api_counts = {app: len(api_set) for app, api_set in app_fingerprinting_data.items()}

    return app_unique_api_counts